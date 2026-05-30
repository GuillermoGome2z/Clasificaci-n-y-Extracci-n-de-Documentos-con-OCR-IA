# 🚀 Despliegue en Streamlit Cloud

## Pasos para desplegar la aplicación en cualquier navegador:

### 1. Prepara tu repositorio GitHub
```bash
git add streamlit_app.py .streamlit/config.toml
git commit -m "Add Streamlit Cloud deployment files"
git push
```

### 2. Accede a Streamlit Cloud
1. Ve a https://streamlit.io/cloud
2. Haz clic en "Sign up with GitHub"
3. Autoriza Streamlit Community Cloud

### 3. Despliega la app
1. Haz clic en "New app"
2. Selecciona tu repositorio: `Clasificaci-n-y-Extracci-n-de-Documentos-con-OCR-IA`
3. Rama: `Teddy` (o la rama actual)
4. Main file path: `streamlit_app.py`
5. Haz clic en "Deploy"

### 4. ¡Listo! 🎉
Tu aplicación estará disponible en una URL como:
```
https://<username>-<project>-<random>.streamlit.app
```

---

## ⚙️ Configuración de Requisitos

El archivo `requirements.txt` incluye todas las dependencias necesarias:
- streamlit (interfaz web)
- pytesseract (OCR)
- scikit-learn (clasificación)
- opencv-python-headless (procesamiento de imágenes)
- Y más...

---

## 📝 Notas Importantes

✅ **Modelos:** Asegúrate de que `models/classifier_model.joblib` esté en el repositorio
✅ **Tesseract:** En Streamlit Cloud, se instala automáticamente
✅ **Datos:** Los archivos de entrenamiento en `data/training/` se incluyen

---

## 🔗 Acceso Remoto

Una vez desplegado, puedes:
- Acceder desde cualquier navegador
- Compartir el enlace con otros
- Usar en dispositivos móviles
- Mantener disponible 24/7 (con limitaciones de recursos gratis)

**Límites Streamlit Cloud (plan gratis):**
- 1 app por cuenta
- 1 GB de almacenamiento
- Reinicio cada 7 días sin actividad
- Recomendado para demostración y desarrollo

---

## 💾 Alternativas si necesitas más poder:

Si necesitas más recursos, considera:
- **Heroku**: Mejor para aplicaciones complejas
- **Google Cloud Run**: Escalable y económico
- **AWS**: Mayor control
- **Azure**: Integración con Microsoft

---

¿Necesitas ayuda con algún paso?
