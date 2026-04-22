"""Módulo de clasificación de documentos con ML."""

from pathlib import Path
from typing import Optional

import joblib
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.naive_bayes import MultinomialNB
from sklearn.pipeline import Pipeline


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
        self.classes = ['factura', 'recibo', 'contrato', 'otro']
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
            self.model_data = joblib.load(path)
            self.classes = self.model_data.get("categories", self.classes)
            self.is_trained = True
        except (OSError, ValueError, EOFError) as e:
            print(f"⚠️  Error cargando modelo entrenado: {e}")
            print("   Usando modelo por defecto (sin entrenar)")
            self._create_default_model()

    def _create_default_model(self):
        """Crea un modelo por defecto sin entrenar."""
        self.pipeline = Pipeline([
            ('tfidf', TfidfVectorizer(max_features=1000, stop_words='spanish')),
            ('classifier', MultinomialNB())
        ])
        self.classes = ['factura', 'recibo', 'contrato', 'otro']
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
            dict: Clase predicha, confianza y probabilidades
        """
        try:
            if self.is_trained and self.model_data:
                # Usar modelo entrenado
                model = self.model_data.get("model")
                vectorizer = self.model_data.get("vectorizer")
                categories = self.model_data.get("categories", self.classes)
                
                X = vectorizer.transform([text])
                predicted_idx = model.predict(X)[0]
                probabilities = model.predict_proba(X)[0]
                
                # Convertir índice a nombre de categoría
                predicted_class = categories[predicted_idx] if predicted_idx < len(categories) else str(predicted_idx)
                
                prob_dict = {
                    categories[i]: float(prob)
                    for i, prob in enumerate(probabilities)
                }
                
                return {
                    "class": predicted_class,
                    "confidence": float(max(probabilities)),
                    "probabilities": prob_dict,
                    "model_type": "trained"
                }
            
            elif self.pipeline:
                # Usar pipeline por defecto
                try:
                    predicted_class = self.pipeline.predict([text])[0]
                    probabilities = self.pipeline.predict_proba([text])[0]
                    
                    prob_dict = {
                        cls: float(prob)
                        for cls, prob in zip(self.pipeline.classes_, probabilities)
                    }
                    
                    return {
                        "class": predicted_class,
                        "confidence": float(max(probabilities)),
                        "probabilities": prob_dict,
                        "model_type": "default (not trained)"
                    }
                except (AttributeError, ValueError):
                    # Pipeline no entrenado
                    return {
                        "class": "desconocido",
                        "confidence": 0.0,
                        "probabilities": {cls: 0.0 for cls in self.classes},
                        "model_type": "untrained"
                    }
            else:
                return {
                    "class": "error",
                    "confidence": 0.0,
                    "error": "No hay modelo disponible"
                }
                
        except (ValueError, AttributeError, IndexError) as e:
            return {
                "class": "error",
                "confidence": 0.0,
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
