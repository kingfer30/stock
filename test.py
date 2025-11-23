import os
import json
import websocket

# 从环境变量中读取 API Key
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

if not OPENAI_API_KEY:
    raise ValueError("请设置 OPENAI_API_KEY 环境变量")

url = "wss://api.openai.com/v1/realtime?model=gpt-realtime"
headers = ["Authorization: Bearer " + OPENAI_API_KEY]


def on_open(ws):
    print("Connected to server.")
    # Send client events over the WebSocket once connected
    ws.send(
        json.dumps(
            {
                "type": "session.update",
                "session": {"type": "realtime", "instructions": "Be extra nice today!"},
            }
        )
    )
    ws.send(
        json.dumps(
            {
                "type": "session.update",
                "session": {"type": "realtime", "instructions": "Be extra nice today!"},
            }
        )
    )
    ws.send(
        json.dumps(
            {
                "type": "conversation.item.create",
                "item": {
                    "type": "message",
                    "role": "user",
                    "content": [{"type": "input_text", "text": "你好, 1+1=?"}],
                },
                "event_id": "b904fba0-0ec4-40af-8bbb-f908a9b26793",
            }
        )
    )


def on_message(ws, message):
    print(message)
    data = json.loads(message)
    print("Received event:", json.dumps(data, indent=2))

def on_data():
     print(message)

ws = websocket.WebSocketApp(
    url,
    header=headers,
    on_open=on_open,
    on_message=on_message,
)

ws.run_forever()
