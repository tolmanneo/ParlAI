source venv/bin/activate
kill $(jobs -p)
python parlai/chat_service/services/browser_chat/run.py --config-path parlai/chat_service/tasks/chatbot/config.yml &
echo "Start websocket server"
jobs
sleep 1
FLASK_APP=parlai/chat_service/services/browser_chat/flask_client.py python -m flask run
