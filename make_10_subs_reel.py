import os
from generate_news_reel import build_news_reel

script_text = (
    "We just hit 10 subscribers on YouTube! A massive thank you to everyone who has supported the channel so far. "
    "This is just the beginning of our journey together. Hit that subscribe button if you haven't already!"
)

headline = "CELEBRATING 10 YOUTUBE SUBSCRIBERS!"
badge_text = "MILESTONE REACHED"
image_path = r"C:\Users\hp\.gemini\antigravity-ide\brain\806ac259-72a3-47d0-99fd-7ad7ca5f9227\youtube_10_subs_1788617267739.jpg"
output_video = "output/celebration_10_subs.mp4"

print("Building celebration reel...")
result = build_news_reel(
    script_text=script_text,
    headline=headline,
    badge_text=badge_text,
    image_path=image_path,
    output_video=output_video
)
if result:
    print(f"Success! Reel saved to {result}")
else:
    print("Failed to build reel.")
