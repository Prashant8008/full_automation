import os
import sys
import time
import requests
from dotenv import load_dotenv

try:
    sys.stdout.reconfigure(encoding="utf-8", line_buffering=True)
except Exception:
    pass

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
load_dotenv(os.path.join(BASE_DIR, ".env"))

access_token = os.environ.get("FACEBOOK_ACCESS_TOKEN")
ig_user_id = os.environ.get("INSTAGRAM_BUSINESS_ACCOUNT_ID")
dry_run = os.environ.get("DRY_RUN", "false").lower() in ("true", "1", "yes")

EXTRA_REELS_DATA = [
    {
        "file": os.path.join(BASE_DIR, "output", "extra_reel_1.mp4"),
        "title": "AI & DIGITALISATION IN THE INDIAN ARMY! 🇮🇳🤖",
        "caption": """AI & DIGITALISATION IN THE INDIAN ARMY! 🇮🇳🤖
📍 Lucknow, India

Lieutenant General Harsh Chhibber addresses officers on the growing role of Artificial Intelligence in modern military operations.
AI and emerging technologies are set to revolutionize operational readiness, tactical decision-making, and intelligence processing across the Armed Forces.

How do you think AI will reshape national defence? Share below! 💬

#IndianArmy #DefenceTech #ArtificialIntelligence #MilitaryAI #IndianArmedForces #DefenceUpdates #SSBConnect
Follow @ssb.connect for daily SSB prep & defence updates."""
    },
    {
        "file": os.path.join(BASE_DIR, "output", "extra_reel_2.mp4"),
        "title": "KEY PROMOTION IN BORDER SECURITY FORCE! 🇮🇳",
        "caption": """KEY PROMOTION IN BORDER SECURITY FORCE! 🇮🇳
📍 New Delhi, India

Director General BSF Praveen Kumar pipped Shri Narendra Singh to the prestigious rank of Deputy Inspector General (DIG) in a piping ceremony at Force Headquarters.
This honors his meritorious service in guarding India's frontiers.

Join us in congratulating the newly promoted DIG! 👏🇮🇳

#BSF #BorderSecurityForce #FirstLineOfDefence #IndianArmedForces #DefenceNews #SSBConnect
Follow @ssb.connect for daily SSB prep & defence updates."""
    },
    {
        "file": os.path.join(BASE_DIR, "output", "extra_reel_3.mp4"),
        "title": "LEADERSHIP TRANSITION AT INHS GOA! ⚓🇮🇳",
        "caption": """LEADERSHIP TRANSITION AT INHS GOA! ⚓🇮🇳
📍 Goa, India

Commodore YV Ramakrishna officially assumes charge as the 29th Officer-in-Charge of naval hospital INHS Goa.
He succeeds Commodore Sajeev K Nair, who retired after 34 years of dedicated commissioned service in the Indian Navy.

Saluting our naval officers for exceptional leadership and medical care! ⚓

#IndianNavy #INHSGoa #NavalOfficers #DefenceUpdates #IndianArmedForces #SSBConnect
Follow @ssb.connect for daily SSB prep & defence updates."""
    }
]


def create_and_upload_reel(video_path, caption):
    if dry_run:
        print(f"[DRY RUN] Would upload reel {video_path}")
        return "MOCK_CONTAINER_ID"
        
    url = f"https://graph.facebook.com/v21.0/{ig_user_id}/media"
    payload = {
        "media_type": "REELS",
        "upload_type": "resumable",
        "access_token": access_token,
        "share_to_feed": "true",
        "caption": caption
    }
    
    res = requests.post(url, data=payload).json()
    if "id" not in res:
        print("Error initializing Reel upload container:", res)
        return None

    container_id = res["id"]
    upload_uri = res.get("uri") or f"https://rupload.facebook.com/ig-api-upload/v21.0/{container_id}"
    file_size = os.path.getsize(video_path)
    
    headers = {
        "Authorization": f"OAuth {access_token}",
        "offset": "0",
        "file_size": str(file_size)
    }
    
    print(f"Streaming {os.path.basename(video_path)} ({file_size / (1024*1024):.2f} MB) to Instagram servers...")
    with open(video_path, "rb") as vf:
        upload_res = requests.post(upload_uri, headers=headers, data=vf, timeout=180)
        if upload_res.status_code not in (200, 201):
            print(f"Direct video upload failed: {upload_res.text}")
            return None

    print(f"Direct video upload complete! Container ID: {container_id}")
    return container_id


def wait_for_container_status(creation_id, max_attempts=15, delay_sec=10):
    if dry_run or not creation_id or creation_id.startswith("MOCK_"):
        return True
    
    url = f"https://graph.facebook.com/v21.0/{creation_id}"
    params = {"fields": "status_code,status", "access_token": access_token}
    
    print(f"Waiting for video processing (container {creation_id})...")
    for attempt in range(1, max_attempts + 1):
        try:
            res = requests.get(url, params=params, timeout=15).json()
            status_code = res.get("status_code", "").upper()
            if status_code == "FINISHED":
                print("Video container processing FINISHED and ready to publish.")
                return True
            elif status_code in ("ERROR", "EXPIRED"):
                print(f"Video processing failed with status: {res}")
                return False
            else:
                print(f"  Status: {status_code or res.get('status', 'IN_PROGRESS')} (attempt {attempt}/{max_attempts})...")
        except Exception as e:
            print(f"  Status check error: {e}")
        time.sleep(delay_sec)
    return False


def publish_container(creation_id):
    if dry_run:
        print(f"[DRY RUN] Published container {creation_id}")
        return "MOCK_POST_ID"
    url = f"https://graph.facebook.com/v21.0/{ig_user_id}/media_publish"
    res = requests.post(url, data={"creation_id": creation_id, "access_token": access_token}).json()
    if "id" in res:
        return res["id"]
    print("Error publishing:", res)
    return None


def main():
    print("\n" + "="*60)
    print("🚀 PUBLISHING 3 NEW LATEST NEWS REELS TO INSTAGRAM")
    print("Interval: 3 minutes (180s) between each reel")
    print("="*60 + "\n")

    for idx, item in enumerate(EXTRA_REELS_DATA, 1):
        if idx > 1:
            print(f"\n⏳ [Anti-Spam] Waiting 3 minutes (180 seconds) before posting Reel {idx}...")
            time.sleep(180)

        print(f"\n▶ [{idx}/3] Uploading: {item['title']}")
        if not os.path.exists(item["file"]):
            print(f"❌ File not found: {item['file']}")
            continue

        cid = create_and_upload_reel(item["file"], item["caption"])
        if cid:
            ready = wait_for_container_status(cid)
            if ready:
                pid = publish_container(cid)
                print(f"✅ Published Reel {idx} to Instagram! Post ID: {pid}")
            else:
                print(f"❌ Failed waiting for Reel container {cid}")

    print("\n🎉 All 3 new latest news reels published to Instagram successfully!\n")


if __name__ == "__main__":
    main()
