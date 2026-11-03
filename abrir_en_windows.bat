@echo off
setlocal enabledelayedexpansion
title EKC (ElektriKubercisC) & Mikel Irastorza · Suite Windows
color 06

:MENU
cls
echo =========================================================================
echo    EKC (ElektriKubercisC) · ARQUITECTURA MULTI-AGENTE Y MATEMATICAS
echo    Lead Systems Architect: Mikel Irastorza (EFA)
echo =========================================================================
echo.
echo   [1] Abrir Portfolio Web y The Brothers (http://127.0.0.1:3222)
echo   [2] Abrir Visualizador de Arquitectura NetGUI (http://127.0.0.1:8765)
echo   [3] Ejecutar Suite de Verificacion de 10 Pasadas (Python)
echo   [4] Ejecutar Tri-Core Matematico (Python + C + Haskell)
echo   [5] Sincronizar Metricas con Bases SQLite de los 9 Agentes
echo   [6] Consultar Estado de Privacidad (publish_live_control.py)
echo   [7] Consultar Estado de IAs Locales (Ollama, Claude, Cursor)
echo   [8] Abrir CV Oficial PWA en Edge/Chrome (Listo para Instalar)
echo   [9] Salir
echo.
echo =========================================================================
set /p OPT="Selecciona una opcion (1-9): "

if "%OPT%"=="1" (
    echo Abriendo Portfolio...
    start http://127.0.0.1:3222/?tab=the-brothers
    pause
    goto MENU
)
if "%OPT%"=="2" (
    echo Abriendo NetGUI Visualizer...
    start http://127.0.0.1:8765
    pause
    goto MENU
)
if "%OPT%"=="3" (
    echo Ejecutando Suite de 10 Pasadas...
    python verify_10_passes.py
    pause
    goto MENU
)
if "%OPT%"=="4" (
    echo Ejecutando Tri-Core Matematico...
    python CV\03_math_haskell_python\ekc_clean_math.py
    pause
    goto MENU
)
if "%OPT%"=="5" (
    echo Sincronizando bases de datos SQLite...
    python sync_ekc_math_to_dbs.py
    pause
    goto MENU
)
if "%OPT%"=="6" (
    echo Consultando privacidad...
    python publish_live_control.py status
    pause
    goto MENU
)
if "%OPT%"=="7" (
    echo Comprobando motores de IA...
    python ekc_ai_bridge.py list
    pause
    goto MENU
)
if "%OPT%"=="8" (
    echo Abriendo CV PWA en Navegador...
    start https://auraicons-studio.vercel.app/cv
    pause
    goto MENU
)
if "%OPT%"=="9" (
    exit /b 0
)

goto MENU
