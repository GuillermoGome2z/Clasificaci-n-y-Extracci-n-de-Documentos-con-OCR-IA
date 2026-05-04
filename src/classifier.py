"""Módulo de clasificación de documentos con ML."""

import logging
from pathlib import Path
from typing import Optional

import joblib
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.svm import LinearSVC
from sklearn.calibration import CalibratedClassifierCV
from sklearn.pipeline import Pipeline

logger = logging.getLogger(__name__)



class DocumentClassifier:
    """Clasifica documentos según su contenido."""

    def __init__(self, model_path: Optional[str] = None):
        """
        Inicializa el clasificador.

        Intenta cargar modelo entrenado. Si no existe, crea uno por defecto sin entrenar.

        Args:
            model_path: Ruta al modelo entrenado (opcional)
        """
        self.model_path = model_path
        self.model_data = None  # Contiene {model, vectorizer, categories, label_mapping}
        self.pipeline = None  # Pipeline por defecto (si no hay modelo entrenado)
        self.classes = ['factura', 'recibo', 'contrato',
                        'constancia', 'carta_formal', 'identificacion', 'otro']
        self.is_trained = False

        # Intentar cargar modelo entrenado
        if model_path and Path(model_path).exists():
            self._load_trained_model(model_path)
        else:
            self._create_default_model()

    def _load_trained_model(self, path: str):
        """
        Carga un modelo entrenado por train_classifier.py

        Args:
            path: Ruta al archivo .joblib del modelo entrenado
        """
        try:
            logger.debug("Intentando cargar modelo desde: %s", path)
            self.model_data = joblib.load(path)
            self.classes = self.model_data.get("categories", self.classes)
            self.is_trained = True
            logger.info("Modelo entrenado cargado exitosamente")
        except (OSError, ValueError, EOFError) as e:
            logger.warning("Error cargando modelo entrenado: %s", e)
            logger.info("Usando modelo por defecto (sin entrenar)")
            self._create_default_model()

    def _create_default_model(self):
        """Crea un modelo por defecto sin entrenar (LinearSVC)."""
        svc = LinearSVC(C=1.0, max_iter=2000, random_state=42)
        self.pipeline = Pipeline([
            ('tfidf', TfidfVectorizer(max_features=5000, ngram_range=(1, 2))),
            ('classifier', CalibratedClassifierCV(svc, cv=3))
        ])
        self.classes = ['factura', 'recibo', 'contrato',
                        'constancia', 'carta_formal', 'identificacion', 'otro']
        self.is_trained = False

    def train(self, texts: list, labels: list):
        """
        Entrena el modelo con textos etiquetados.

        Args:
            texts: Lista de textos de entrenamiento
            labels: Lista de etiquetas correspondientes
        """
        if not self.pipeline:
            self._create_default_model()

        self.classes = list(set(labels))
        self.pipeline.fit(texts, labels)  # type: ignore

    def predict(self, text: str) -> dict:
        """
        Predice la clase de un documento.

        Args:
            text: Texto del documento

        Returns:
            dict: Clase predicha, confianza, probabilidades y estado del modelo
        """
        try:
            if self.is_trained and self.model_data:
                # Usar modelo entrenado
                logger.debug("Usando modelo ENTRENADO para predicción")
                model = self.model_data.get("model")
                vectorizer = self.model_data.get("vectorizer")
                categories = self.model_data.get("categories", self.classes)

                X = vectorizer.transform([text])
                raw_pred = model.predict(X)[0]
                probabilities = model.predict_proba(X)[0]

                # El modelo puede devolver el label directamente (str) o un índice (int)
                if isinstance(raw_pred, (int, np.integer)):
                    predicted_class = categories[int(raw_pred)] if int(raw_pred) < len(categories) else str(raw_pred)
                else:
                    predicted_class = str(raw_pred)

                # Mapear probabilidades usando model.classes_ si está disponible
                model_classes = list(getattr(model, "classes_", categories))
                prob_dict = {
                    str(cls): float(prob)
                    for cls, prob in zip(model_classes, probabilities)
                }

                result = {
                    "predicted_class": predicted_class,  # Compatibilidad histórica
                    "class": predicted_class,            # Alias moderno
                    "confidence": float(max(probabilities)),
                    "probabilities": prob_dict,
                    "model_type": "trained",
                    "is_trained": True
                }
                logger.info("Predicción exitosa: %s (confianza: %.2f)", predicted_class, result["confidence"])
                return result

            if self.pipeline:
                # Usar pipeline por defecto (sin entrenar)
                logger.warning("Modelo NO ENTRENADO. Usando pipeline por defecto (predicciones poco confiables)")
                try:
                    predicted_class = self.pipeline.predict([text])[0]
                    probabilities = self.pipeline.predict_proba([text])[0]

                    prob_dict = {
                        cls: float(prob)
                        for cls, prob in zip(self.pipeline.classes_, probabilities)
                    }

                    result = {
                        "predicted_class": predicted_class,  # Compatibilidad histórica
                        "class": predicted_class,            # Alias moderno
                        "confidence": float(max(probabilities)),
                        "probabilities": prob_dict,
                        "model_type": "default (not trained)",
                        "is_trained": False,
                        "warning": "Modelo no entrenado. Esta predicción tiene baja confianza. Por favor, entrena el modelo con train_classifier.py"
                    }
                    logger.debug("Predicción por defecto devuelta (NO ENTRENADO)")
                    return result
                except (AttributeError, ValueError) as e:
                    # Pipeline no entrenado
                    logger.error("Error usando pipeline: %s", e)
                    return {
                        "predicted_class": "desconocido",  # Compatibilidad histórica
                        "class": "desconocido",            # Alias moderno
                        "confidence": 0.0,
                        "probabilities": {cls: 0.0 for cls in self.classes},
                        "model_type": "untrained",
                        "is_trained": False,
                        "warning": "Error: No hay modelo disponible. Por favor, entrena el modelo."
                    }
            else:
                logger.error("No hay modelo disponible en el sistema")
                return {
                    "predicted_class": "error",  # Compatibilidad histórica
                    "class": "error",            # Alias moderno
                    "confidence": 0.0,
                    "is_trained": False,
                    "error": "No hay modelo disponible"
                }

        except (ValueError, AttributeError, IndexError) as e:
            logger.error("Excepción en predict(): %s", e)
            return {
                "predicted_class": "error",  # Compatibilidad histórica
                "class": "error",            # Alias moderno
                "confidence": 0.0,
                "is_trained": False,
                "error": str(e)
            }

    def predict_batch(self, texts: list) -> list:
        """
        Predice clases para múltiples textos.

        Args:
            texts: Lista de textos

        Returns:
            Lista de predicciones
        """
        return [self.predict(text) for text in texts]

    def save_model(self, path: str):
        """
        Guarda el modelo entrenado.

        Args:
            path: Ruta para guardar el modelo
        """
        if self.model_data:
            joblib.dump(self.model_data, path)
        elif self.pipeline:
            joblib.dump(self.pipeline, path)

    def load_model(self, path: str):
        """
        Carga un modelo entrenado.

        Args:
            path: Ruta al modelo
        """
        if Path(path).exists():
            self._load_trained_model(path)

    def get_feature_importance(self, class_label: Optional[str] = None, top_n: int = 10) -> dict:
        """
        Obtiene las palabras más importantes para cada clase.

        Args:
            class_label: Clase específica (opcional)
            top_n: Número de palabras a retornar

        Returns:
            dict: Palabras importantes por clase
        """
        if not self.pipeline or not hasattr(self.pipeline.named_steps['classifier'], 'coef_'):
            return {}

        feature_names = self.pipeline.named_steps['tfidf'].get_feature_names_out()
        coef = self.pipeline.named_steps['classifier'].coef_

        importance = {}

        if class_label:
            class_idx = list(self.pipeline.classes_).index(class_label)
            top_indices = np.argsort(coef[class_idx])[-top_n:]
            importance[class_label] = [feature_names[i] for i in reversed(top_indices)]
        else:
            for i, cls in enumerate(self.pipeline.classes_):
                top_indices = np.argsort(coef[i])[-top_n:]
                importance[cls] = [feature_names[idx] for idx in reversed(top_indices)]

        return importance
