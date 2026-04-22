"""
Validador de Dataset - Analiza estructura y calidad de datos de entrenamiento

Responsabilidades:
- Verificar estructura de directorios (data/training/<categoría>/)
- Contar documentos por categoría
- Detectar problemas (falta de datos, categorías vacías)
- Generar reporte visual para usuario
- Validar formatos de archivo

Uso:
    from src.dataset_validator import DatasetValidator
    validator = DatasetValidator()
    report = validator.validate()
    print(report.summary())
"""

import json
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Dict, List


@dataclass
class ValidationIssue:
    """Problema detectado en dataset."""
    severity: str  # "error", "warning", "info"
    category: str
    message: str


@dataclass
class CategoryStats:
    """Estadísticas de una categoría."""
    name: str
    file_count: int
    total_words: int
    avg_words_per_file: float
    min_words: int
    max_words: int


class DatasetValidator:
    """Validador completo del dataset de entrenamiento."""
    
    CATEGORIES = ["factura", "recibo", "contrato", "otro"]
    MIN_RECOMMENDED_PER_CATEGORY = 50  # Recomendado para buena accuracy
    MIN_VIABLE_PER_CATEGORY = 20  # Mínimo para entrenar
    MIN_WORDS_PER_FILE = 50  # Archivo muy corto
    MAX_WORDS_PER_FILE = 50000  # Archivo muy largo (probablemente error)
    
    def __init__(self, data_dir: Path = None):
        """
        Args:
            data_dir: Ruta a data/training/. Si no se proporciona, auto-detecta.
        """
        if data_dir is None:
            data_dir = Path(__file__).parent.parent / "data" / "training"
        
        self.data_dir = data_dir
        self.issues: List[ValidationIssue] = []
        self.category_stats: Dict[str, CategoryStats] = {}
        self.total_documents = 0
        self.total_words = 0
    
    def validate(self) -> 'ValidationReport':
        """
        Ejecuta validación completa del dataset.
        
        Returns:
            ValidationReport con resultados y recomendaciones.
        """
        self.issues.clear()
        self.category_stats.clear()
        self.total_documents = 0
        self.total_words = 0
        
        # Paso 1: Verificar que directorio existe
        if not self.data_dir.exists():
            self.issues.append(ValidationIssue(
                severity="error",
                category="structure",
                message=f"Directorio no existe: {self.data_dir}"
            ))
            return ValidationReport(self)
        
        # Paso 2: Verificar que existen categorías
        existing_categories = [d for d in self.data_dir.iterdir() if d.is_dir()]
        if not existing_categories:
            self.issues.append(ValidationIssue(
                severity="error",
                category="structure",
                message=f"No hay carpetas de categorías en {self.data_dir}"
            ))
            return ValidationReport(self)
        
        # Paso 3: Validar cada categoría
        for category in self.CATEGORIES:
            self._validate_category(category)
        
        # Paso 4: Validaciones globales
        self._validate_global_stats()
        
        return ValidationReport(self)
    
    def _validate_category(self, category: str) -> None:
        """Valida una categoría específica."""
        category_dir = self.data_dir / category
        
        # ¿Existe la carpeta?
        if not category_dir.exists():
            self.issues.append(ValidationIssue(
                severity="warning",
                category=category,
                message=f"Carpeta no existe: {category_dir}"
            ))
            self.category_stats[category] = CategoryStats(
                name=category,
                file_count=0,
                total_words=0,
                avg_words_per_file=0,
                min_words=0,
                max_words=0
            )
            return
        
        # Contar archivos .txt
        txt_files = list(category_dir.glob("*.txt"))
        file_count = len(txt_files)
        
        if file_count == 0:
            self.issues.append(ValidationIssue(
                severity="error",
                category=category,
                message=f"Sin archivos .txt en {category}/"
            ))
            self.category_stats[category] = CategoryStats(
                name=category,
                file_count=0,
                total_words=0,
                avg_words_per_file=0,
                min_words=0,
                max_words=0
            )
            return
        
        # Analizar contenido
        word_counts = []
        total_words = 0
        
        for txt_file in txt_files:
            try:
                content = txt_file.read_text(encoding='utf-8').strip()
                word_count = len(content.split())
                word_counts.append(word_count)
                total_words += word_count
                
                # Validar tamaño de archivo
                if word_count < self.MIN_WORDS_PER_FILE:
                    self.issues.append(ValidationIssue(
                        severity="warning",
                        category=category,
                        message=f"{txt_file.name}: muy corto ({word_count} palabras)"
                    ))
                elif word_count > self.MAX_WORDS_PER_FILE:
                    self.issues.append(ValidationIssue(
                        severity="warning",
                        category=category,
                        message=f"{txt_file.name}: muy largo ({word_count} palabras)"
                    ))
                
            except Exception as e:
                self.issues.append(ValidationIssue(
                    severity="error",
                    category=category,
                    message=f"{txt_file.name}: error lectura - {str(e)}"
                ))
        
        # Guardar estadísticas
        avg_words = total_words / file_count if file_count > 0 else 0
        self.category_stats[category] = CategoryStats(
            name=category,
            file_count=file_count,
            total_words=total_words,
            avg_words_per_file=avg_words,
            min_words=min(word_counts) if word_counts else 0,
            max_words=max(word_counts) if word_counts else 0
        )
        
        self.total_documents += file_count
        self.total_words += total_words
        
        # Validar cantidad de archivos
        if file_count < self.MIN_VIABLE_PER_CATEGORY:
            self.issues.append(ValidationIssue(
                severity="warning",
                category=category,
                message=f"Solo {file_count} docs (mín viable: {self.MIN_VIABLE_PER_CATEGORY})"
            ))
        
        if file_count < self.MIN_RECOMMENDED_PER_CATEGORY:
            self.issues.append(ValidationIssue(
                severity="info",
                category=category,
                message=f"Solo {file_count} docs (recomendado: {self.MIN_RECOMMENDED_PER_CATEGORY})"
            ))
    
    def _validate_global_stats(self) -> None:
        """Validaciones sobre estadísticas globales."""
        # Verificar balance de categorías
        file_counts = [stats.file_count for stats in self.category_stats.values()]
        
        if file_counts and max(file_counts) > 0:
            max_count = max(file_counts)
            min_count = min(file_counts)
            
            if max_count > min_count * 3:
                self.issues.append(ValidationIssue(
                    severity="info",
                    category="balance",
                    message=f"Dataset desbalanceado: máx={max_count}, mín={min_count}"
                ))


class ValidationReport:
    """Reporte de validación del dataset."""
    
    def __init__(self, validator: DatasetValidator):
        self.validator = validator
        self.timestamp = __import__('datetime').datetime.now().isoformat()
    
    def summary(self) -> str:
        """Resumen breve para mostrar en CLI."""
        lines = []
        lines.append("=" * 70)
        lines.append("📊 VALIDACIÓN DE DATASET")
        lines.append("=" * 70)
        
        # Estadísticas globales
        lines.append(f"\n📁 Directorio: {self.validator.data_dir}")
        lines.append(f"📄 Total de documentos: {self.validator.total_documents}")
        lines.append(f"💬 Total de palabras: {self.validator.total_words:,}")
        
        # Por categoría
        lines.append("\n📋 Documentos por categoría:")
        for category in self.validator.CATEGORIES:
            stats = self.validator.category_stats.get(category)
            if stats and stats.file_count > 0:
                lines.append(
                    f"   • {category:10} : {stats.file_count:3} docs "
                    f"({stats.total_words:6,} palabras, "
                    f"promedio: {stats.avg_words_per_file:.0f})"
                )
            elif stats:
                lines.append(f"   • {category:10} : ❌ SIN DATOS")
        
        # Problemas
        if self.validator.issues:
            lines.append("\n⚠️  PROBLEMAS DETECTADOS:")
            errors = [i for i in self.validator.issues if i.severity == "error"]
            warnings = [i for i in self.validator.issues if i.severity == "warning"]
            infos = [i for i in self.validator.issues if i.severity == "info"]
            
            for issue in errors:
                lines.append(f"   ❌ [{issue.category}] {issue.message}")
            for issue in warnings:
                lines.append(f"   ⚠️  [{issue.category}] {issue.message}")
            for issue in infos:
                lines.append(f"   ℹ️  [{issue.category}] {issue.message}")
        else:
            lines.append("\n✅ Sin problemas detectados")
        
        # Recomendaciones
        lines.append("\n💡 RECOMENDACIONES:")
        if self.validator.total_documents == 0:
            lines.append("   • Crear datos en data/training/<categoría>/")
        elif self.validator.total_documents < 80:
            lines.append(f"   • Agregar más datos ({self.validator.total_documents}/80 recomendados)")
        else:
            lines.append(f"   • Dataset tiene buen tamaño ({self.validator.total_documents} docs)")
        
        accuracy_estimate = self._estimate_accuracy()
        lines.append(f"   • Accuracy esperado: ~{accuracy_estimate}% (con estos datos)")
        
        if self.validator.total_documents >= 20:
            lines.append("   • LISTO PARA ENTRENAR ✅")
        else:
            lines.append("   • Faltan datos para entrenar de forma confiable")
        
        lines.append("=" * 70)
        return "\n".join(lines)
    
    def _estimate_accuracy(self) -> int:
        """Estima accuracy basado en cantidad de datos."""
        # Heurística simple: más datos = más accuracy
        # Basado en empiria del proyecto
        total = self.validator.total_documents
        
        if total < 20:
            return 40  # Muy poco
        elif total < 50:
            return 60  # Poco
        elif total < 100:
            return 75  # Medio
        elif total < 200:
            return 85  # Bueno
        else:
            return 90  # Excelente
    
    def to_dict(self) -> dict:
        """Convierte reporte a diccionario (para JSON)."""
        return {
            "timestamp": self.timestamp,
            "total_documents": self.validator.total_documents,
            "total_words": self.validator.total_words,
            "categories": {
                cat: asdict(stats)
                for cat, stats in self.validator.category_stats.items()
            },
            "issues": [
                {
                    "severity": issue.severity,
                    "category": issue.category,
                    "message": issue.message
                }
                for issue in self.validator.issues
            ],
            "recommended_accuracy": self._estimate_accuracy()
        }
    
    def save(self, filepath: Path) -> None:
        """Guarda reporte en JSON."""
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(self.to_dict(), f, indent=2, ensure_ascii=False)


# Función de utilidad
def validate_dataset(data_dir: Path = None) -> ValidationReport:
    """Función helper para validar dataset rápidamente."""
    validator = DatasetValidator(data_dir)
    return validator.validate()
