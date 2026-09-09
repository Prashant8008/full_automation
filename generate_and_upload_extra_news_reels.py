import os
import sys
import time

try:
    sys.stdout.reconfigure(encoding="utf-8")
except Exception:
    pass

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, BASE_DIR)

from generate_news_reel import build_news_reel
from publish_to_youtube import upload_short

EXTRA_NEWS = [
    {
        "id": 4,
        "badge": "TECH & DEFENCE",
        "headline": "LT GEN HARSH CHHIBBER HIGHLIGHTS ROLE OF AI IN FUTURE ARMY OPERATIONS",
        "script": "Digitalisation and Artificial Intelligence are transforming modern warfare! Lieutenant General Harsh Chhibber highlighted how AI and emerging technologies enhance operational effectiveness and strategic decision-making for the Indian Army. Follow for daily defence updates!",
        "title": "Lt Gen Harsh Chhibber Highlights AI in Future Indian Army Operations #Shorts",
        "description": "Lt Gen Harsh Chhibber addresses officers on leveraging AI, data analytics, and modern tech for military dominance.\n\n#Shorts #IndianArmy #DefenceTech #AINews #Military",
        "bg_image": "assets/defence_soldiers.png",
        "output": "output/extra_reel_1.mp4"
    },
    {
        "id": 5,
        "badge": "BSF PROMOTION",
        "headline": "DG BSF PRAVEEN KUMAR PIPS NARENDRA SINGH TO DEPUTY INSPECTOR GENERAL",
        "script": "Key leadership promotion in the Border Security Force! DG BSF Praveen Kumar pipped Narendra Singh to the rank of Deputy Inspector General in New Delhi, honoring his meritorious service in securing national borders. Follow for daily defence updates!",
        "title": "DG BSF Praveen Kumar Pips Narendra Singh to Rank of DIG #Shorts",
        "description": "BSF honors Commandant Narendra Singh with promotion to DIG at Force Headquarters in New Delhi.\n\n#Shorts #BSF #IndianForces #BorderSecurity #Defence",
        "bg_image": "assets/defence_soldiers.png",
        "output": "output/extra_reel_2.mp4"
    },
    {
        "id": 6,
        "badge": "NAVY UPDATE",
        "headline": "COMMODORE YV RAMAKRISHNA TAKES OVER AS OFFICER-IN-CHARGE OF INHS GOA",
        "script": "Key leadership transition in naval healthcare! Hydrography specialist Commodore YV Ramakrishna has officially taken over as the 29th Officer-in-Charge of INHS Goa, succeeding Commodore Sajeev Nair. Follow for daily defence updates!",
        "title": "Commodore YV Ramakrishna Takes Over as 29th OIC of INHS Goa #Shorts",
        "description": "Commodore YV Ramakrishna assumes charge of naval hospital INHS Goa following 34 years of commissioned service by predecessor.\n\n#Shorts #IndianNavy #INHSGoa #DefenceNews",
        "bg_image": "assets/defence_navy.png",
        "output": "output/extra_reel_3.mp4"
    }
]

def main():
    print(f"\n{'='*70}")
    print("🎬 RENDERING & UPLOADING 3 ADDITIONAL LATEST NEWS SHORTS TO YOUTUBE")
    print(f"{'='*70}\n")

    uploaded = []

    for idx, item in enumerate(EXTRA_NEWS, 1):
        print(f"\n--- [Step 1/{len(EXTRA_NEWS)}] Rendering Reel {idx}: {item['badge']} ---")
        
        # 1. Render Video Reel
        vid_path = build_news_reel(
            script_text=item["script"],
            headline=item["headline"],
            badge_text=item["badge"],
            image_path=item["bg_image"],
            output_video=item["output"]
        )

        if not vid_path or not os.path.exists(vid_path):
            print(f"❌ Failed to render {item['output']}")
            continue

        print(f"✅ Video ready: {vid_path}")
        time.sleep(1)

        # 2. Upload to YouTube Shorts
        print(f"\n--- [Step 2/{len(EXTRA_NEWS)}] Uploading Reel {idx} to YouTube Shorts ---")
        res = upload_short(
            video_path=vid_path,
            title=item["title"],
            description=item["description"],
            privacy_status="public"
        )

        if res:
            vid_id = res.get("id")
            uploaded.append({
                "title": item["title"],
                "id": vid_id,
                "url": f"https://www.youtube.com/shorts/{vid_id}"
            })

    print(f"\n{'='*70}")
    print(f"🎉 COMPLETED: Uploaded {len(uploaded)} additional News Shorts to YouTube!")
    for u in uploaded:
        print(f"• {u['title']}: {u['url']}")
    print(f"{'='*70}\n")

if __name__ == "__main__":
    main()
