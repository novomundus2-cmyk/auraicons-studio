#!/usr/bin/env bash
# =========================================================================
# EKC (ElektriKubercisC) & Mikel Irastorza · Suite macOS / Linux
# =========================================================================

show_menu() {
    clear
    echo "========================================================================="
    echo "   EKC (ElektriKubercisC) · ARQUITECTURA MULTI-AGENTE Y MATEMÁTICAS     "
    echo "   Lead Systems Architect: Mikel Irastorza (EFA)                        "
    echo "========================================================================="
    echo ""
    echo "   [1] Abrir Portfolio Web y The Brothers (http://127.0.0.1:3222)        "
    echo "   [2] Abrir Visualizador NetGUI (http://127.0.0.1:8765)                "
    echo "   [3] Ejecutar Suite de Verificación de 10 Pasadas (Python)            "
    echo "   [4] Ejecutar Tri-Core Matemático (Python + C + Haskell)              "
    echo "   [5] Sincronizar Métricas con Bases SQLite de los 9 Agentes           "
    echo "   [6] Consultar Estado de Privacidad (publish_live_control.py)         "
    echo "   [7] Consultar Estado de IAs Locales (Ollama, Claude, Cursor)         "
    echo "   [8] Abrir CV PWA en Navegador (Listo para Instalar)                  "
    echo "   [9] Salir                                                            "
    echo ""
    echo "========================================================================="
    read -p "Selecciona una opción (1-9): " opt
}

while true; do
    show_menu
    case $opt in
        1)
            echo "Abriendo Portfolio..."
            if command -v open >/dev/null 2>&1; then
                open "http://127.0.0.1:3222/?tab=the-brothers"
            elif command -v xdg-open >/dev/null 2>&1; then
                xdg-open "http://127.0.0.1:3222/?tab=the-brothers"
            fi
            read -p "Presiona Enter para continuar..."
            ;;
        2)
            echo "Abriendo NetGUI..."
            if command -v open >/dev/null 2>&1; then
                open "http://127.0.0.1:8765"
            elif command -v xdg-open >/dev/null 2>&1; then
                xdg-open "http://127.0.0.1:8765"
            fi
            read -p "Presiona Enter para continuar..."
            ;;
        3)
            python3 verify_10_passes.py
            read -p "Presiona Enter para continuar..."
            ;;
        4)
            python3 CV/03_math_haskell_python/ekc_clean_math.py
            read -p "Presiona Enter para continuar..."
            ;;
        5)
            python3 sync_ekc_math_to_dbs.py
            read -p "Presiona Enter para continuar..."
            ;;
        6)
            python3 publish_live_control.py status
            read -p "Presiona Enter para continuar..."
            ;;
        7)
            python3 ekc_ai_bridge.py list
            read -p "Presiona Enter para continuar..."
            ;;
        8)
            if command -v open >/dev/null 2>&1; then
                open "https://auraicons-studio.vercel.app/cv"
            elif command -v xdg-open >/dev/null 2>&1; then
                xdg-open "https://auraicons-studio.vercel.app/cv"
            fi
            read -p "Presiona Enter para continuar..."
            ;;
        9)
            exit 0
            ;;
        *)
            echo "Opción no válida."
            sleep 1
            ;;
    esac
done
