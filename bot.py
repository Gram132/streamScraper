import os
import time
import requests
import re
from downloader import cut_and_watermark_kick_video
from list_video_from_drive import list_videos_in_folder



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
    # Dummy function – replace this with your own logic
    print(f"Scraping from {url}, start='{start}', end='{end}', name='{name}'")
    cut_and_watermark_kick_video(
        m3u8_url=url,
        start_time=start,
        end_time=end,
        logo_path="./logo/logo.png",
        streamer_name=name,
        font_path="./font/Merriweather.ttf"
    )

    return f"✅ End Scraping ...."

# Validation functions
def is_valid_url(url):
    return url.startswith("http://") or url.startswith("https://")

def is_valid_time_format(value):
    return re.match(r"^\d{2}:\d{2}:\d{2}$", value) is not None

def is_valid_name(name):
    #return name.replace(" ", "").isalpha()
    return True

# Handle each incoming message
def handle_message(chat_id, text):
    state = user_states.get(chat_id)

    if text == "/listvideos":
        user_states[chat_id] = "awaiting_listvideos"
        user_data[chat_id] = {}
        send_message(chat_id, "📥 Working on list video files . please wait.")
        
    if text == "/scrape":
        user_states[chat_id] = "awaiting_url"
        user_data[chat_id] = {}
        send_message(chat_id, "📥 Please send the URL to scrape:")

    elif state == "awaiting_url":
        if is_valid_url(text):
            user_data[chat_id]["url"] = text
            user_states[chat_id] = "awaiting_start"
            send_message(chat_id, "⏱️ Enter the start time (HH:MM:SS):")
        else:
            send_message(chat_id, "❌ Invalid URL. It must start with http:// or https://")

    elif state == "awaiting_start":
        if is_valid_time_format(text):
            user_data[chat_id]["start"] = text
            user_states[chat_id] = "awaiting_end"
            send_message(chat_id, "⏱️ Enter the end time (HH:MM:SS):")
        else:
            send_message(chat_id, "❌ Invalid format. Use HH:MM:SS (e.g., 00:05:30).")

    elif state == "awaiting_end":
        if is_valid_time_format(text):
            user_data[chat_id]["end"] = text
            user_states[chat_id] = "awaiting_name"
            send_message(chat_id, "💾 Enter a name to save the result (letters only):")
        else:
            send_message(chat_id, "❌ Invalid format. Use HH:MM:SS (e.g., 00:07:45).")

    elif state == "awaiting_name":
        if is_valid_name(text):
            user_data[chat_id]["name"] = text
            data = user_data[chat_id]
            send_message(chat_id, f"✅ Starting to scrape from {data['start']} to {data['end']}, saving as: {data['name']}")
            
            result = scrape_data(data["url"], data["start"], data["end"], data["name"])
            send_message(chat_id, result)
            user_states.pop(chat_id)
            user_data.pop(chat_id)
        else:
            send_message(chat_id, "❌ Invalid name. Use letters only (no numbers or symbols).")
    
    elif state == "awaiting_listvideos":
        FOLDER_ID = "1gz_hpSSr0f73scjkwAE5XfH1zSrj60sT"
        videos = list_videos_in_folder(FOLDER_ID)
        
        if not videos:
            print("❌ No video files found in the folder.")
        else:
            print(f"📁 Found {len(videos)} video(s):\n")
            for file in videos:
                name = file['name']
                file_id = file['id']
                url = f"https://drive.google.com/file/d/{file_id}/view"
                print(f"🎥 {name}\n🔗 {url}\n")
                send_message(f"🎥 {name}\n🔗 {url}\n")
    else:
        send_message(chat_id, f"🤖 Send /scrape to begin scraping or /listvideos to list all videos in the folder. ")

# Main polling loop
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
