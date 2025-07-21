import os
import time
import requests

TOKEN = os.getenv("BOT_TOKEN")
URL = f"https://api.telegram.org/bot{TOKEN}/"

user_states = {}
user_data = {}

def get_updates(offset=None):
    response = requests.get(URL + "getUpdates", params={"offset": offset})
    return response.json()

def send_message(chat_id, text):
    requests.post(URL + "sendMessage", data={"chat_id": chat_id, "text": text})

def scrape_data(url, start, end, name):
    # Dummy function – replace with your logic
    print(f"Scraping from {url}, start='{start}', end='{end}', saving as '{name}'")
    return f"Scraped data saved as {name}!"

def handle_message(chat_id, text):
    state = user_states.get(chat_id)

    if text == "/scrape":
        user_states[chat_id] = "awaiting_url"
        user_data[chat_id] = {}
        send_message(chat_id, "Please send the URL to scrape:")
    elif state == "awaiting_url":
        user_data[chat_id]["url"] = text
        user_states[chat_id] = "awaiting_start"
        send_message(chat_id, "Enter the start tag:")
    elif state == "awaiting_start":
        user_data[chat_id]["start"] = text
        user_states[chat_id] = "awaiting_end"
        send_message(chat_id, "Enter the end tag:")
    elif state == "awaiting_end":
        user_data[chat_id]["end"] = text
        user_states[chat_id] = "awaiting_name"
        send_message(chat_id, "Enter the name to save the result:")
    elif state == "awaiting_name":
        user_data[chat_id]["name"] = text
        data = user_data[chat_id]
        result = scrape_data(data["url"], data["start"], data["end"], data["name"])
        send_message(chat_id, result)
        user_states.pop(chat_id)
        user_data.pop(chat_id)
    else:
        send_message(chat_id, "Send /scrape to start scraping.")

def main():
    offset = None
    while True:
        updates = get_updates(offset)
        if "result" in updates:
            for update in updates["result"]:
                if "message" in update and "text" in update["message"]:
                    chat_id = update["message"]["chat"]["id"]
                    text = update["message"]["text"]
                    handle_message(chat_id, text)
                    offset = update["update_id"] + 1
        time.sleep(2)

if __name__ == "__main__":
    main()
