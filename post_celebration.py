import os
from publish_to_telegram import send_telegram_video, CHAT_ID, BOT_TOKEN

video_path = "output/celebration_10_subs.mp4"
caption = "🎉 We just hit 10 subscribers on YouTube! 🎉\n\nA massive thank you to everyone who has supported the channel so far. This is just the beginning of our journey together. Hit that subscribe button if you haven't already!"

if not BOT_TOKEN or not CHAT_ID:
    print("Telegram credentials not found.")
else:
    print(f"Sending to chat {CHAT_ID}...")
    success = send_telegram_video(CHAT_ID, video_path, caption=caption)
    if success:
        print("Successfully posted to Telegram!")
    else:
        print("Failed to post.")
