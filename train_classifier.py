"""
Script de entrenamiento para el clasificador de documentos.

Entrena un modelo Naive Bayes + TF-IDF con datos de training.
Datos esperados en: data/training/<categoría>/*.txt

Uso:
    python train_classifier.py

Requisitos:
    - scikit-learn, joblib ya instalados
    - Archivos .txt en data/training/<categoría>/

Salida:
    - models/classifier_model.joblib (modelo entrenado)
"""

import os
import sys
from pathlib import Path
import json
from datetime import datetime

# Agregar raíz al path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.naive_bayes import MultinomialNB
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, classification_report, confusion_matrix
import joblib

from config import DATA_DIR, MODELS_DIR, CLASSIFIER_CONFIG


class ClassifierTrainer:
    """Entrenador del clasificador de documentos."""
    
    # Categorías soportadas
    CATEGORIES = ["factura", "recibo", "contrato", "otro"]
    
    def __init__(self):
        """Inicializa el entrenador."""
        self.data_dir = Path(DATA_DIR) / "training"
        self.models_dir = Path(MODELS_DIR)
        self.model_path = self.models_dir / "classifier_model.joblib"
        self.vectorizer = TfidfVectorizer(
            max_features=CLASSIFIER_CONFIG.get("max_features", 5000),
            ngram_range=(1, 2),
            min_df=2,
            max_df=0.8
        )
        self.model = MultinomialNB()
        self.texts = []
        self.labels = []
        self.label_mapping = {cat: i for i, cat in enumerate(self.CATEGORIES)}
        
    def load_training_data(self) -> bool:
        """
        Carga archivos de entrenamiento desde data/training/<categoría>/*.txt
        
        Returns:
            bool: True si se cargaron datos, False si no hay datos
        """
        print(f"📂 Buscando datos en: {self.data_dir}")
        
        if not self.data_dir.exists():
            print(f"⚠️  Directorio no existe: {self.data_dir}")
            return False
        
        total_files = 0
        
        for category in self.CATEGORIES:
            category_dir = self.data_dir / category
            if not category_dir.exists():
                print(f"   ⚠️  {category}/: directorio no encontrado")
                continue
            
            files = list(category_dir.glob("*.txt"))
            print(f"   📄 {category}/: {len(files)} archivo(s)")
            
            for file_path in files:
                try:
                    with open(file_path, "r", encoding="utf-8") as f:
                        text = f.read().strip()
                    
                    if text:  # Solo si tiene contenido
                        self.texts.append(text)
                        self.labels.append(self.label_mapping[category])
                        total_files += 1
                except Exception as e:
                    print(f"      ❌ Error leyendo {file_path.name}: {e}")
        
        print(f"\n✅ Total archivos cargados: {total_files}")
        
        if total_files == 0:
            print("❌ No hay archivos de entrenamiento. Agrega .txt en data/training/")
            return False
        
        return True
    
    def train(self) -> dict:
        """
        Entrena el modelo.
        
        Returns:
            dict: Métricas de entrenamiento
        """
        print("\n🔄 Preparando datos...")
        
        # Calcular test_size dinámico para pocos datos
        total_samples = len(self.texts)
        min_per_class = min([self.labels.count(i) for i in set(self.labels)])
        
        # Si hay muy pocos datos, usar un split más pequeño
        if total_samples < 20:
            test_size = 0.2  # Mínimo 20% para validación
        elif min_per_class < 3:
            test_size = 0.2
        else:
            test_size = 0.2
        
        # Convertir test_size a mínimo de 1 muestra por clase
        test_samples = max(1, int(total_samples * test_size))
        
        print(f"   - Entrenamiento: ~{total_samples - test_samples} muestras")
        print(f"   - Validación: ~{test_samples} muestras")
        
        # Split train/test con stratify solo si hay suficientes muestras
        try:
            X_train, X_test, y_train, y_test = train_test_split(
                self.texts, self.labels, test_size=test_size, random_state=42, stratify=self.labels
            )
        except ValueError:
            # Fallback sin stratify si hay muy pocos datos
            X_train, X_test, y_train, y_test = train_test_split(
                self.texts, self.labels, test_size=test_size, random_state=42
            )
        
        # Vectorización TF-IDF
        print("⚙️  Extrayendo características (TF-IDF)...")
        X_train_vec = self.vectorizer.fit_transform(X_train)
        X_test_vec = self.vectorizer.transform(X_test)
        
        print(f"   - Vocabulario: {len(self.vectorizer.get_feature_names_out())} términos")
        
        # Entrenamiento
        print("🤖 Entrenando Naive Bayes...")
        self.model.fit(X_train_vec, y_train)
        
        # Evaluación
        print("📊 Evaluando modelo...")
        y_pred = self.model.predict(X_test_vec)
        accuracy = accuracy_score(y_test, y_pred)
        
        print(f"\n✨ Accuracy: {accuracy:.2%}")
        
        # Reporte detallado
        print("\n📈 Reporte de Clasificación:")
        class_report = classification_report(
            y_test, y_pred, 
            target_names=self.CATEGORIES,
            digits=3
        )
        print(class_report)
        
        # Matriz de confusión
        print("Matriz de Confusión:")
        cm = confusion_matrix(y_test, y_pred)
        print("  ", "  ".join(f"{cat:8}" for cat in self.CATEGORIES))
        for i, cat in enumerate(self.CATEGORIES):
            print(f"{cat:8}", cm[i])
        
        return {
            "accuracy": float(accuracy),
            "samples_train": len(X_train),
            "samples_test": len(X_test),
            "vocab_size": len(self.vectorizer.get_feature_names_out()),
            "confusion_matrix": cm.tolist(),
            "trained_at": datetime.now().isoformat()
        }
    
    def save_model(self) -> bool:
        """
        Guarda el modelo y vectorizador en models/
        
        Returns:
            bool: True si se guardó exitosamente
        """
        print(f"\n💾 Guardando modelo en {self.model_path}...")
        
        try:
            self.models_dir.mkdir(parents=True, exist_ok=True)
            
            # Guardar como un único archivo con ambos objetos
            model_data = {
                "model": self.model,
                "vectorizer": self.vectorizer,
                "categories": self.CATEGORIES,
                "label_mapping": self.label_mapping,
                "trained_at": datetime.now().isoformat()
            }
            
            joblib.dump(model_data, self.model_path)
            print(f"✅ Modelo guardado exitosamente")
            
            # Info del archivo
            size_mb = self.model_path.stat().st_size / (1024 * 1024)
            print(f"   📦 Tamaño: {size_mb:.2f} MB")
            
            return True
        except Exception as e:
            print(f"❌ Error al guardar modelo: {e}")
            return False
    
    def create_summary(self, metrics: dict):
        """Crea un reporte de resumen."""
        summary = {
            "timestamp": datetime.now().isoformat(),
            "training_status": "success",
            "metrics": metrics,
            "categories": self.CATEGORIES,
            "data_path": str(self.data_dir),
            "model_path": str(self.model_path)
        }
        return summary


def main():
    """Función principal."""
    print("=" * 70)
    print("🎓 ENTRENADOR DE CLASIFICADOR DE DOCUMENTOS")
    print("=" * 70)
    
    trainer = ClassifierTrainer()
    
    # Cargar datos
    if not trainer.load_training_data():
        print("\n⚠️  No se puede continuar sin datos de entrenamiento.")
        print(f"   Agrega archivos .txt en: {trainer.data_dir}")
        print("   Ver: data/training/README.md para instrucciones")
        return 1
    
    # Entrenar
    try:
        metrics = trainer.train()
        
        # Guardar
        if not trainer.save_model():
            return 1
        
        # Resumen
        summary = trainer.create_summary(metrics)
        print("\n" + "=" * 70)
        print("✨ ENTRENAMIENTO COMPLETADO EXITOSAMENTE")
        print("=" * 70)
        print(f"📊 Accuracy: {metrics['accuracy']:.2%}")
        print(f"📚 Muestras: {metrics['samples_train']} (entrenamiento) + {metrics['samples_test']} (validación)")
        print(f"🎯 Categorías: {len(trainer.CATEGORIES)}")
        print(f"💾 Modelo: {trainer.model_path}")
        
        return 0
        
    except Exception as e:
        print(f"\n❌ Error durante el entrenamiento: {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())
