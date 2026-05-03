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
    - models/training_metrics.json (métricas del entrenamiento)
"""

import sys
import json
from pathlib import Path
from datetime import datetime

# Agregar raíz al path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.svm import LinearSVC
from sklearn.calibration import CalibratedClassifierCV
from sklearn.model_selection import train_test_split, cross_val_score
from sklearn.metrics import accuracy_score, classification_report, confusion_matrix
import joblib

from config import DATA_DIR, MODELS_DIR, CLASSIFIER_CONFIG
from src.dataset_validator import validate_dataset


class ClassifierTrainer:
    """Entrenador del clasificador de documentos."""
    
    # Categorías soportadas (7 según enunciado oficial)
    CATEGORIES = ["factura", "recibo", "contrato",
                  "constancia", "carta_formal", "identificacion", "otro"]
    
    def __init__(self):
        """Inicializa el entrenador."""
        self.data_dir = Path(DATA_DIR) / "training"
        self.models_dir = Path(MODELS_DIR)
        self.model_path = self.models_dir / "classifier_model.joblib"
        self.metrics_path = self.models_dir / "training_metrics.json"
        self.vectorizer = TfidfVectorizer(
            max_features=CLASSIFIER_CONFIG.get("max_features", 5000),
            ngram_range=(1, 2),
            min_df=2,
            max_df=0.8
        )
        # LinearSVC con CalibratedClassifierCV para obtener probabilidades
        svc = LinearSVC(C=1.0, max_iter=2000, random_state=42)
        self.model = CalibratedClassifierCV(svc, cv=5)
        self.texts = []
        self.labels = []
        self.label_mapping = {cat: i for i, cat in enumerate(self.CATEGORIES)}
        self.total_documents = 0
        
    def validate_dataset(self) -> bool:
        """
        Valida dataset antes de entrenar.
        
        Returns:
            bool: True si dataset es válido, False en caso contrario
        """
        print("\n🔍 Validando dataset...")
        report = validate_dataset(self.data_dir.parent)
        print(report.summary())
        
        # Guardar validación
        validation_path = self.models_dir / "dataset_validation.json"
        self.models_dir.mkdir(parents=True, exist_ok=True)
        report.save(validation_path)
        print(f"\n✅ Validación guardada en {validation_path}")
        
        # Retornar True solo si hay suficientes datos
        return self.total_documents >= 20 if hasattr(self, 'total_documents') else True
        
    def load_training_data(self) -> bool:
        """
        Carga archivos de entrenamiento desde data/training/<categoría>/*.txt
        
        Returns:
            bool: True si se cargaron datos, False si no hay datos
        """
        print(f"\n📂 Buscando datos en: {self.data_dir}")
        
        if not self.data_dir.exists():
            print(f"⚠️  Directorio no existe: {self.data_dir}")
            return False
        
        total_files = 0
        category_counts = {}
        
        for category in self.CATEGORIES:
            category_dir = self.data_dir / category
            if not category_dir.exists():
                print(f"   ⚠️  {category}/: directorio no encontrado")
                category_counts[category] = 0
                continue
            
            files = list(category_dir.glob("*.txt"))
            category_counts[category] = len(files)
            print(f"   📄 {category:10}: {len(files):2} archivo(s)", end="")
            
            category_words = 0
            for file_path in files:
                try:
                    with open(file_path, "r", encoding="utf-8") as f:
                        text = f.read().strip()
                    
                    if text:  # Solo si tiene contenido
                        self.texts.append(text)
                        self.labels.append(self.label_mapping[category])
                        total_files += 1
                        category_words += len(text.split())
                except (OSError, UnicodeDecodeError) as e:
                    print(f"      ❌ Error leyendo {file_path.name}: {e}")
            
            if len(files) > 0:
                print(f"  ({category_words:,} palabras)")
            else:
                print()
        
        print(f"\n✅ Total archivos cargados: {total_files}")
        
        if total_files == 0:
            print("❌ No hay archivos de entrenamiento. Agrega .txt en data/training/")
            return False
        
        self.total_documents = total_files
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
        except ValueError as e:
            # Fallback sin stratify si hay muy pocos datos por clase
            import logging as _logging
            _logging.getLogger(__name__).warning(
                "Stratified split falló (%s). Usando split sin stratify — métricas pueden estar sesgadas.", e
            )
            X_train, X_test, y_train, y_test = train_test_split(
                self.texts, self.labels, test_size=test_size, random_state=42
            )
        
        # Vectorización TF-IDF
        print("\n⚙️  Extrayendo características (TF-IDF)...")
        X_train_vec = self.vectorizer.fit_transform(X_train)
        X_test_vec = self.vectorizer.transform(X_test)
        
        vocab_size = len(self.vectorizer.get_feature_names_out())
        print(f"   - Vocabulario: {vocab_size:,} términos únicos")
        
        # Entrenamiento
        print("\n🤖 Entrenando Naive Bayes Multinomial...")
        self.model.fit(X_train_vec, y_train)
        print("   ✅ Modelo entrenado")
        
        # Evaluación
        print("\n📊 Evaluando modelo...")
        y_pred = self.model.predict(X_test_vec)
        accuracy = accuracy_score(y_test, y_pred)
        
        print(f"\n{'=' * 70}")
        print(f"✨ ACCURACY: {accuracy:.2%}")
        print(f"{'=' * 70}")
        
        # Reporte detallado
        print("\n📈 REPORTE DE CLASIFICACIÓN")
        print("-" * 70)
        class_report = classification_report(
            y_test, y_pred, 
            target_names=self.CATEGORIES,
            digits=4
        )
        print(class_report)
        
        # Matriz de confusión
        print("📊 MATRIZ DE CONFUSIÓN")
        print("-" * 70)
        cm = confusion_matrix(y_test, y_pred)
        
        # Header con nombres de categoría
        print("      Predicción →")
        print("  Real", "  ".join(f"{cat:10}" for cat in self.CATEGORIES))
        for i, cat in enumerate(self.CATEGORIES):
            row_str = f"{cat:5} " + "  ".join(f"{cm[i][j]:>9}" for j in range(len(self.CATEGORIES)))
            print(row_str)
        print()
        
        metrics = {
            "accuracy": float(accuracy),
            "samples_train": len(X_train),
            "samples_test": len(X_test),
            "vocab_size": vocab_size,
            "total_samples": len(self.texts),
            "accuracy_percent": f"{accuracy*100:.2f}%",
            "confusion_matrix": cm.tolist(),
            "classification_report": classification_report(
                y_test, y_pred, 
                target_names=self.CATEGORIES,
                output_dict=True
            ),
            "trained_at": datetime.now().isoformat()
        }
        
        return metrics
    
    def save_model(self) -> bool:
        """
        Guarda el modelo y vectorizador en models/
        
        Returns:
            bool: True si se guardó exitosamente
        """
        print("\n💾 GUARDANDO MODELO")
        print(f"   Ruta: {self.model_path}")
        
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
            
            # Info del archivo
            size_kb = self.model_path.stat().st_size / 1024
            print(f"   ✅ Modelo guardado: {size_kb:.1f} KB")
            
            return True
        except (OSError, ValueError) as e:
            print(f"   ❌ Error al guardar: {e}")
            return False
    
    def save_metrics(self, metrics: dict) -> bool:
        """
        Guarda métricas del entrenamiento en JSON.
        
        Returns:
            bool: True si se guardó exitosamente
        """
        print("\n📊 GUARDANDO MÉTRICAS")
        
        try:
            self.models_dir.mkdir(parents=True, exist_ok=True)
            
            with open(self.metrics_path, 'w', encoding='utf-8') as f:
                json.dump(metrics, f, indent=2, ensure_ascii=False)
            
            print(f"   ✅ Métricas guardadas: {self.metrics_path}")
            return True
        except (OSError, TypeError) as e:
            print(f"   ❌ Error al guardar métricas: {e}")
            return False
        
    def create_summary(self, metrics: dict):
        """Crea un reporte de resumen."""
        summary = {
            "timestamp": datetime.now().isoformat(),
            "training_status": "success",
            "metrics": metrics,
            "categories": self.CATEGORIES,
            "data_path": str(self.data_dir),
            "model_path": str(self.model_path),
            "metrics_path": str(self.metrics_path)
        }
        return summary


def main():
    """Función principal."""
    print("=" * 70)
    print("🎓 ENTRENADOR DE CLASIFICADOR DE DOCUMENTOS")
    print("=" * 70)
    
    trainer = ClassifierTrainer()
    
    # Paso 1: Validar dataset
    print("\n" + "=" * 70)
    print("PASO 1: VALIDACIÓN DE DATASET")
    print("=" * 70)
    trainer.validate_dataset()
    
    # Paso 2: Cargar datos
    print("\n" + "=" * 70)
    print("PASO 2: CARGA DE DATOS")
    print("=" * 70)
    if not trainer.load_training_data():
        print("\n⚠️  No se puede continuar sin datos de entrenamiento.")
        print(f"   Agrega archivos .txt en: {trainer.data_dir}")
        print("   Ver: data/training/README.md para instrucciones")
        return 1
    
    # Paso 3: Entrenar
    print("\n" + "=" * 70)
    print("PASO 3: ENTRENAMIENTO")
    print("=" * 70)
    metrics = trainer.train()
    
    # Paso 4: Guardar
    print("\n" + "=" * 70)
    print("PASO 4: PERSISTENCIA")
    print("=" * 70)
    
    if not trainer.save_model():
        return 1
    
    if not trainer.save_metrics(metrics):
        return 1
    
    # Resumen final
    print("\n" + "=" * 70)
    print("✅ ENTRENAMIENTO COMPLETADO EXITOSAMENTE")
    print("=" * 70)
    print(f"\n📦 Modelo: {trainer.model_path}")
    print(f"📊 Métricas: {trainer.metrics_path}")
    print(f"✨ Accuracy logrado: {metrics['accuracy_percent']}")
    print("\nPróximo paso: Usar el modelo en app.py o pipeline")
    print("=" * 70)
    
    return 0


if __name__ == "__main__":
    sys.exit(main())
