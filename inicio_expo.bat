@echo off
REM ════════════════════════════════════════════════════════════════
REM  SISTEMA INTELIGENTE OCR + IA
REM  Launcher para EXPO - Un clic y todo funciona
REM ════════════════════════════════════════════════════════════════
REM

title OCR IA - Sistema Inteligente (EXPO)
color 0A

echo.
echo  ════════════════════════════════════════════════════════════
echo   SISTEMA INTELIGENTE OCR + IA
echo   Iniciando aplicacion para EXPO...
echo  ════════════════════════════════════════════════════════════
echo.

REM Ir a la carpeta del proyecto
cd /d "%~dp0"

REM Activar venv
call venv\Scripts\activate.bat 2>nul

if errorlevel 1 (
    echo  [ERROR] No se pudo activar venv
    echo  Por favor, verifica que venv existe
    pause
    exit /b 1
)

echo  [OK] Entorno virtual activado
echo.
echo  [..] Verificando sistema... (esto tarda 10-15 segundos)
echo.

REM Ejecutar verificacion
python verificar_expo.py

echo.
echo  ════════════════════════════════════════════════════════════
echo   [OK] Sistema listo para EXPO
echo   [..] Abriendo aplicacion en el navegador...
echo  ════════════════════════════════════════════════════════════
echo.
echo   URL: http://localhost:8501
echo.
echo   Si el navegador no abre automaticamente, visita la URL arriba.
echo   Para detener: Cierra esta ventana o presiona Ctrl+C
echo.
echo  ════════════════════════════════════════════════════════════
echo.

REM Ejecutar streamlit
python -m streamlit run app/app.py ^
    --server.port 8501 ^
    --browser.gatherUsageStats false ^
    --client.showErrorDetails true

REM Si streamlit se cierra, esperar a que el usuario lo vea
pause
