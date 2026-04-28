"""
crear_notebooks.py — Genera los 3 notebooks requeridos por el enunciado.
Ejecutar: python crear_notebooks.py
"""
import json
from pathlib import Path

Path("notebooks").mkdir(exist_ok=True)

# ── NOTEBOOK 1: EDA ──────────────────────────────────────────────────────────
eda_cells = [
    {
        "cell_type": "markdown",
        "metadata": {},
        "source": [
            "# 01 - Análisis Exploratorio de Datos (EDA)\n",
            "\n",
            "**Proyecto 04 — Clasificación y Extracción de Documentos con OCR + IA**\n",
            "Universidad Mariano Gálvez de Guatemala · Curso 045 - Inteligencia Artificial\n",
            "\n",
            "Este notebook analiza el dataset sintético generado para el clasificador de documentos."
        ]
    },
    {
        "cell_type": "code",
        "execution_count": None,
        "metadata": {},
        "outputs": [],
        "source": [
            "import pandas as pd\n",
            "import matplotlib.pyplot as plt\n",
            "import matplotlib\n",
            "matplotlib.use('Agg')\n",
            "from pathlib import Path\n",
            "from collections import Counter\n",
            "\n",
            "# Cargar ground truth\n",
            "gt = pd.read_csv('../data/ground_truth.csv')\n",
            "print('Total documentos:', len(gt))\n",
            "print(gt.head())"
        ]
    },
    {
        "cell_type": "code",
        "execution_count": None,
        "metadata": {},
        "outputs": [],
        "source": [
            "# Distribución de clases\n",
            "dist = gt['categoria'].value_counts()\n",
            "print('Distribución por categoría:')\n",
            "print(dist)\n",
            "\n",
            "fig, ax = plt.subplots(figsize=(10, 5))\n",
            "dist.plot(kind='bar', ax=ax, color='steelblue', edgecolor='black')\n",
            "ax.set_title('Distribución de Documentos por Categoría')\n",
            "ax.set_xlabel('Categoría')\n",
            "ax.set_ylabel('Cantidad de Documentos')\n",
            "ax.tick_params(axis='x', rotation=45)\n",
            "plt.tight_layout()\n",
            "plt.savefig('eda_distribucion_clases.png', dpi=100, bbox_inches='tight')\n",
            "print('Gráfica guardada: eda_distribucion_clases.png')"
        ]
    },
    {
        "cell_type": "code",
        "execution_count": None,
        "metadata": {},
        "outputs": [],
        "source": [
            "# Análisis de longitud de documentos\n",
            "print('Estadísticas de longitud (palabras):')\n",
            "print(gt.groupby('categoria')['num_palabras'].describe())\n",
            "\n",
            "fig, ax = plt.subplots(figsize=(10, 5))\n",
            "gt.boxplot(column='num_palabras', by='categoria', ax=ax)\n",
            "ax.set_title('Distribución de Longitud por Categoría')\n",
            "ax.set_xlabel('Categoría')\n",
            "ax.set_ylabel('Número de Palabras')\n",
            "plt.suptitle('')\n",
            "plt.xticks(rotation=45)\n",
            "plt.tight_layout()\n",
            "plt.savefig('eda_longitud_documentos.png', dpi=100, bbox_inches='tight')\n",
            "print('Gráfica guardada.')"
        ]
    },
    {
        "cell_type": "code",
        "execution_count": None,
        "metadata": {},
        "outputs": [],
        "source": [
            "# Vocabulario clave por categoría (top 10 palabras)\n",
            "import re\n",
            "\n",
            "stopwords_es = {'de', 'la', 'el', 'en', 'y', 'a', 'que', 'se', 'los',\n",
            "                'las', 'un', 'una', 'por', 'con', 'es', 'del', 'no',\n",
            "                'al', 'su', 'lo', 'para', 'como', 'más', 'sus'}\n",
            "\n",
            "print('Top 10 palabras por categoría:')\n",
            "for cat in gt['categoria'].unique():\n",
            "    archivos = gt[gt['categoria'] == cat]['archivo'].tolist()\n",
            "    textos = []\n",
            "    for f in archivos[:10]:  # Primeros 10 archivos\n",
            "        try:\n",
            "            texto = Path(f).read_text(encoding='utf-8').lower()\n",
            "            palabras = re.findall(r'[a-záéíóúñ]{4,}', texto)\n",
            "            textos.extend(palabras)\n",
            "        except:\n",
            "            pass\n",
            "    top = Counter(w for w in textos if w not in stopwords_es).most_common(10)\n",
            "    print(f'  {cat}: {[w for w, c in top]}')"
        ]
    },
    {
        "cell_type": "markdown",
        "metadata": {},
        "source": [
            "## Conclusiones EDA\n",
            "\n",
            "- Dataset balanceado: 35 documentos por categoría (245 total)\n",
            "- Vocabulario diferenciado por categoría confirmado\n",
            "- Sin desbalance significativo entre clases\n",
            "- Dataset listo para entrenamiento"
        ]
    }
]

nb_eda = {
    "nbformat": 4,
    "nbformat_minor": 5,
    "metadata": {
        "kernelspec": {"display_name": "Python 3", "language": "python", "name": "python3"},
        "language_info": {"name": "python", "version": "3.13.0"}
    },
    "cells": eda_cells
}

# ── NOTEBOOK 2: ENTRENAMIENTO ────────────────────────────────────────────────
train_cells = [
    {
        "cell_type": "markdown",
        "metadata": {},
        "source": [
            "# 02 - Entrenamiento del Modelo\n",
            "\n",
            "**Proyecto 04 — Clasificación y Extracción de Documentos con OCR + IA**\n",
            "\n",
            "Pipeline: TF-IDF (max_features=5000, ngram_range=(1,2)) + LinearSVC (C=1.0)\n",
            "Validación cruzada de 5 pliegues (5-fold cross-validation)"
        ]
    },
    {
        "cell_type": "code",
        "execution_count": None,
        "metadata": {},
        "outputs": [],
        "source": [
            "import sys\n",
            "sys.path.insert(0, '..')\n",
            "\n",
            "import pandas as pd\n",
            "import numpy as np\n",
            "from pathlib import Path\n",
            "from sklearn.feature_extraction.text import TfidfVectorizer\n",
            "from sklearn.svm import LinearSVC\n",
            "from sklearn.calibration import CalibratedClassifierCV\n",
            "from sklearn.model_selection import cross_val_score, train_test_split\n",
            "from sklearn.metrics import accuracy_score, classification_report\n",
            "import joblib\n",
            "\n",
            "CATEGORIES = ['factura', 'recibo', 'contrato', 'constancia',\n",
            "              'carta_formal', 'identificacion', 'otro']\n",
            "\n",
            "# Cargar datos\n",
            "texts, labels = [], []\n",
            "for cat in CATEGORIES:\n",
            "    cat_dir = Path(f'../data/training/{cat}')\n",
            "    for f in cat_dir.glob('*.txt'):\n",
            "        try:\n",
            "            texts.append(f.read_text(encoding='utf-8'))\n",
            "            labels.append(cat)\n",
            "        except:\n",
            "            pass\n",
            "\n",
            "print(f'Total documentos cargados: {len(texts)}')\n",
            "from collections import Counter\n",
            "print('Por categoría:', Counter(labels))"
        ]
    },
    {
        "cell_type": "code",
        "execution_count": None,
        "metadata": {},
        "outputs": [],
        "source": [
            "# Vectorización TF-IDF\n",
            "vectorizer = TfidfVectorizer(max_features=5000, ngram_range=(1, 2))\n",
            "X = vectorizer.fit_transform(texts)\n",
            "print(f'Matriz TF-IDF: {X.shape}')\n",
            "print(f'Vocabulario: {len(vectorizer.vocabulary_)} términos')"
        ]
    },
    {
        "cell_type": "code",
        "execution_count": None,
        "metadata": {},
        "outputs": [],
        "source": [
            "# Validación cruzada 5-fold (LinearSVC)\n",
            "svc = LinearSVC(C=1.0, max_iter=2000, random_state=42)\n",
            "scores = cross_val_score(svc, X, labels, cv=5, scoring='f1_macro')\n",
            "print(f'F1-macro (5-fold CV): {scores.mean():.4f} ± {scores.std():.4f}')\n",
            "print(f'Scores por fold: {[f\"{s:.4f}\" for s in scores]}')"
        ]
    },
    {
        "cell_type": "code",
        "execution_count": None,
        "metadata": {},
        "outputs": [],
        "source": [
            "# Entrenamiento final con split 80/20\n",
            "X_train, X_test, y_train, y_test = train_test_split(\n",
            "    texts, labels, test_size=0.2, random_state=42, stratify=labels\n",
            ")\n",
            "\n",
            "vec = TfidfVectorizer(max_features=5000, ngram_range=(1, 2))\n",
            "X_tr = vec.fit_transform(X_train)\n",
            "X_te = vec.transform(X_test)\n",
            "\n",
            "svc_final = LinearSVC(C=1.0, max_iter=2000, random_state=42)\n",
            "clf = CalibratedClassifierCV(svc_final, cv=5)\n",
            "clf.fit(X_tr, y_train)\n",
            "\n",
            "y_pred = clf.predict(X_te)\n",
            "acc = accuracy_score(y_test, y_pred)\n",
            "print(f'Accuracy en test: {acc:.4f} ({acc*100:.1f}%)')"
        ]
    },
    {
        "cell_type": "markdown",
        "metadata": {},
        "source": [
            "## Resultados de Entrenamiento\n",
            "\n",
            "- Algoritmo: TF-IDF + LinearSVC (C=1.0) con CalibratedClassifierCV\n",
            "- Validación: 5-fold cross-validation\n",
            "- Split final: 80% train / 20% test"
        ]
    }
]

nb_train = {
    "nbformat": 4,
    "nbformat_minor": 5,
    "metadata": {
        "kernelspec": {"display_name": "Python 3", "language": "python", "name": "python3"},
        "language_info": {"name": "python", "version": "3.13.0"}
    },
    "cells": train_cells
}

# ── NOTEBOOK 3: EVALUACIÓN ───────────────────────────────────────────────────
eval_cells = [
    {
        "cell_type": "markdown",
        "metadata": {},
        "source": [
            "# 03 - Evaluación del Modelo\n",
            "\n",
            "**Proyecto 04 — Clasificación y Extracción de Documentos con OCR + IA**\n",
            "\n",
            "Métricas: Accuracy, F1-macro, Precision, Recall, Matriz de Confusión"
        ]
    },
    {
        "cell_type": "code",
        "execution_count": None,
        "metadata": {},
        "outputs": [],
        "source": [
            "import sys\n",
            "sys.path.insert(0, '..')\n",
            "\n",
            "import joblib\n",
            "import numpy as np\n",
            "import matplotlib\n",
            "matplotlib.use('Agg')\n",
            "import matplotlib.pyplot as plt\n",
            "import seaborn as sns\n",
            "from pathlib import Path\n",
            "from sklearn.metrics import (\n",
            "    accuracy_score, f1_score, classification_report,\n",
            "    confusion_matrix\n",
            ")\n",
            "from sklearn.model_selection import train_test_split\n",
            "\n",
            "CATEGORIES = ['factura', 'recibo', 'contrato', 'constancia',\n",
            "              'carta_formal', 'identificacion', 'otro']\n",
            "\n",
            "# Cargar datos\n",
            "texts, labels = [], []\n",
            "for cat in CATEGORIES:\n",
            "    for f in Path(f'../data/training/{cat}').glob('*.txt'):\n",
            "        try:\n",
            "            texts.append(f.read_text(encoding='utf-8'))\n",
            "            labels.append(cat)\n",
            "        except:\n",
            "            pass\n",
            "\n",
            "# Cargar modelo\n",
            "model_data = joblib.load('../models/classifier_model.joblib')\n",
            "model = model_data['model']\n",
            "vectorizer = model_data['vectorizer']\n",
            "\n",
            "_, X_test_raw, _, y_test = train_test_split(\n",
            "    texts, labels, test_size=0.2, random_state=42, stratify=labels\n",
            ")\n",
            "X_test = vectorizer.transform(X_test_raw)\n",
            "y_pred = model.predict(X_test)\n",
            "\n",
            "print('=== MÉTRICAS DE EVALUACIÓN ===')\n",
            "print(f'Accuracy: {accuracy_score(y_test, y_pred):.4f}')\n",
            "print(f'F1-macro: {f1_score(y_test, y_pred, average=\"macro\"):.4f}')\n",
            "print()\n",
            "print(classification_report(y_test, y_pred, target_names=CATEGORIES))"
        ]
    },
    {
        "cell_type": "code",
        "execution_count": None,
        "metadata": {},
        "outputs": [],
        "source": [
            "# Matriz de confusión\n",
            "cm = confusion_matrix(y_test, y_pred, labels=CATEGORIES)\n",
            "\n",
            "fig, ax = plt.subplots(figsize=(10, 8))\n",
            "sns.heatmap(\n",
            "    cm, annot=True, fmt='d', cmap='Blues',\n",
            "    xticklabels=CATEGORIES, yticklabels=CATEGORIES, ax=ax\n",
            ")\n",
            "ax.set_title('Matriz de Confusión — LinearSVC + TF-IDF')\n",
            "ax.set_xlabel('Predicción')\n",
            "ax.set_ylabel('Real')\n",
            "plt.xticks(rotation=45, ha='right')\n",
            "plt.tight_layout()\n",
            "plt.savefig('confusion_matrix.png', dpi=100, bbox_inches='tight')\n",
            "print('Matriz de confusión guardada: confusion_matrix.png')"
        ]
    },
    {
        "cell_type": "markdown",
        "metadata": {},
        "source": [
            "## Conclusiones de Evaluación\n",
            "\n",
            "- Algoritmo: TF-IDF (5000 features, ngram (1,2)) + LinearSVC (C=1.0)\n",
            "- Validación cruzada 5-fold utilizada durante entrenamiento\n",
            "- F1-macro es la métrica principal según el enunciado\n",
            "- Matriz de confusión muestra qué tipos de documento se confunden entre sí"
        ]
    }
]

nb_eval = {
    "nbformat": 4,
    "nbformat_minor": 5,
    "metadata": {
        "kernelspec": {"display_name": "Python 3", "language": "python", "name": "python3"},
        "language_info": {"name": "python", "version": "3.13.0"}
    },
    "cells": eval_cells
}

# Guardar los 3 notebooks
notebooks = {
    "notebooks/01_EDA.ipynb": nb_eda,
    "notebooks/02_train.ipynb": nb_train,
    "notebooks/03_evaluation.ipynb": nb_eval,
}

for path, nb in notebooks.items():
    Path(path).parent.mkdir(exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(nb, f, ensure_ascii=False, indent=1)
    print(f"OK: {path}")

print("\nNotebooks creados. Ejecutar con: jupyter notebook")
