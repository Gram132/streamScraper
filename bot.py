import os
import time
import requests

TOKEN = os.getenv("BOT_TOKEN")
URL = f"https://api.telegram.org/bot{TOKEN}/"

def get_updates(offset=None):
    response = requests.get(URL + "getUpdates", params={"offset": offset})
    return response.json()

def send_message(chat_id, text):
    requests.post(URL + "sendMessage", data={"chat_id": chat_id, "text": text})

def main():
    offset = None
    while True:
        updates = get_updates(offset)
        if "result" in updates:
            for update in updates["result"]:
                chat_id = update["message"]["chat"]["id"]
                text = update["message"]["text"]
                send_message(chat_id, f"You said: {text}")
                offset = update["update_id"] + 1
        time.sleep(2)

if __name__ == "__main__":
    main()
