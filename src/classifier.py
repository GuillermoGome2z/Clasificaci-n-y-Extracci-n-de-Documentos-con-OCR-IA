"""Módulo de clasificación de documentos con ML."""

import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.naive_bayes import MultinomialNB
from sklearn.pipeline import Pipeline
import joblib
from pathlib import Path


class DocumentClassifier:
    """Clasifica documentos según su contenido."""

    def __init__(self, model_path: str = None):
        """
        Inicializa el clasificador.
        
        Args:
            model_path: Ruta al modelo entrenado (opcional)
        """
        self.model_path = model_path
        self.pipeline = None
        self.classes = None
        
        if model_path and Path(model_path).exists():
            self.load_model(model_path)
        else:
            self._create_default_model()

    def _create_default_model(self):
        """Crea un modelo por defecto sin entrenar."""
        self.pipeline = Pipeline([
            ('tfidf', TfidfVectorizer(max_features=1000, stop_words='spanish')),
            ('classifier', MultinomialNB())
        ])
        self.classes = ['factura', 'recibo', 'contrato', 'otro']

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
        self.pipeline.fit(texts, labels)

    def predict(self, text: str) -> dict:
        """
        Predice la clase de un documento.
        
        Args:
            text: Texto del documento
            
        Returns:
            dict: Clase predicha y confianza
        """
        if not self.pipeline:
            return {
                "class": "desconocido",
                "confidence": 0.0,
                "probabilities": {}
            }
        
        try:
            # Predicción
            predicted_class = self.pipeline.predict([text])[0]
            
            # Probabilidades
            probabilities = self.pipeline.predict_proba([text])[0]
            
            # Crear diccionario de probabilidades
            prob_dict = {
                cls: float(prob)
                for cls, prob in zip(self.pipeline.classes_, probabilities)
            }
            
            return {
                "class": predicted_class,
                "confidence": float(max(probabilities)),
                "probabilities": prob_dict
            }
        except Exception as e:
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
        if self.pipeline:
            joblib.dump(self.pipeline, path)
            joblib.dump(self.classes, path.replace('.pkl', '_classes.pkl'))

    def load_model(self, path: str):
        """
        Carga un modelo entrenado.
        
        Args:
            path: Ruta al modelo
        """
        try:
            self.pipeline = joblib.load(path)
            classes_path = path.replace('.pkl', '_classes.pkl')
            if Path(classes_path).exists():
                self.classes = joblib.load(classes_path)
        except Exception as e:
            print(f"Error al cargar modelo: {e}")
            self._create_default_model()

    def get_feature_importance(self, class_label: str = None, top_n: int = 10) -> dict:
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
