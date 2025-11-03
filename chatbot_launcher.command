#!/bin/bash

clear
echo "DIVINE TRIBE CHATBOT LAUNCHER"
echo "=============================="
echo ""
echo "[1] 🤖 AI Mode (chatbot_modular.py)"
echo "[2] 👤 Human Mode (chatbot_with_human.py)"
echo "[3] 🔄 Quick Switch"
echo "[Q] Quit"
echo ""
read -p "Choose: " choice

cd "/Users/matthewmacosko/Desktop/dataset for Tribe Chatbot"
source venv/bin/activate

case $choice in
    1)
        echo "Starting AI Mode..."
        python3 chatbot_modular.py
        ;;
    2)
        echo "Starting Human Mode..."
        osascript -e 'tell app "Terminal" to do script "cd \"/Users/matthewmacosko/Desktop/dataset for Tribe Chatbot\" && source venv/bin/activate && python telegram_bot_listener.py"'
        sleep 2
        python3 chatbot_with_human.py
        ;;
    3)
        pkill -f "chatbot_modular.py"
        pkill -f "chatbot_with_human.py"
        echo "Killed all chatbots. Run again to start fresh."
        ;;
    [Qq])
        echo "Bye!"
        ;;
esac
