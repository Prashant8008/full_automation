import os
import sys
import json
import pickle
import argparse
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload

try:
    sys.stdout.reconfigure(encoding="utf-8")
except Exception:
    pass

from brand_utils import clean_article_text

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
SCOPES = ["https://www.googleapis.com/auth/youtube.upload"]
TOKEN_PATH = os.path.join(BASE_DIR, "youtube_token.pickle")
CLIENT_SECRETS_FILE = os.path.join(BASE_DIR, "client_secret.json")


def get_authenticated_service():
    """Authenticates the user with YouTube OAuth 2.0."""
    creds = None
    if os.path.exists(TOKEN_PATH):
        with open(TOKEN_PATH, "rb") as token:
            creds = pickle.load(token)

    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
            with open(TOKEN_PATH, "wb") as token:
                pickle.dump(creds, token)
        else:
            if not os.path.exists(CLIENT_SECRETS_FILE):
                raise FileNotFoundError(f"Missing {CLIENT_SECRETS_FILE}")
            flow = InstalledAppFlow.from_client_secrets_file(CLIENT_SECRETS_FILE, SCOPES)
            creds = flow.run_local_server(port=0)
            with open(TOKEN_PATH, "wb") as token:
                pickle.dump(creds, token)

    return build("youtube", "v3", credentials=creds)


def upload_short(
    video_path: str,
    title: str,
    description: str = "",
    tags: list = None,
    privacy_status: str = "public"
):
    """Uploads a video to YouTube Shorts."""
    if not os.path.isabs(video_path):
        video_path = os.path.join(BASE_DIR, video_path)

    if not os.path.exists(video_path):
        print(f"❌ [YouTube Shorts] File not found: {video_path}")
        return None

    # Title max 100 chars, YouTube forbids < and >
    clean_title = clean_article_text(title.replace("<", "").replace(">", "").strip())
    clean_description = clean_article_text(description)
    if "#Shorts" not in clean_title:
        clean_title = f"{clean_title} #Shorts"
    if len(clean_title) > 95:
        # Keep clean cut before words
        clean_title = clean_title[:85].rsplit(" ", 1)[0] + " #Shorts"

    if tags is None:
        tags = ["Shorts", "DefenceNews", "IndianArmy", "CurrentAffairs", "SSBPrep", "Military"]

    # Ensure description has #Shorts
    if "#Shorts" not in clean_description:
        clean_description = f"{clean_description}\n\n#Shorts #Defence #IndianArmedForces #SSB"

    youtube = get_authenticated_service()

    body = {
        "snippet": {
            "title": clean_title,
            "description": clean_description.strip(),
            "tags": tags,
            "categoryId": "25",  # 25 = News & Politics, 28 = Science & Tech
        },
        "status": {
            "privacyStatus": privacy_status,
            "selfDeclaredMadeForKids": False
        }
    }

    media = MediaFileUpload(
        video_path,
        chunksize=5 * 1024 * 1024,
        resumable=True,
        mimetype="video/mp4"
    )

    request = youtube.videos().insert(
        part="snippet,status",
        body=body,
        media_body=media
    )

    print(f"\n▶ Uploading Short: '{clean_title}'")
    print(f"  File: {video_path}")
    print(f"  Visibility: {privacy_status}")

    response = None
    while response is None:
        status, response = request.next_chunk()
        if status:
            print(f"  Upload progress: {int(status.progress() * 100)}%")

    video_id = response.get("id")
    shorts_url = f"https://www.youtube.com/shorts/{video_id}"
    print(f"✅ Upload Complete!")
    print(f"🎬 Video ID: {video_id}")
    print(f"🔗 Link: {shorts_url}\n")
    return response


def get_post_metadata():
    """Extract titles and descriptions from daily plan & newscards."""
    items = []
    plan_file = os.path.join(BASE_DIR, "daily_post_plan.json")
    if os.path.exists(plan_file):
        try:
            with open(plan_file, "r", encoding="utf-8") as f:
                plan = json.load(f)
                news = plan.get("news_assignments", [])
                for idx, n in enumerate(news, 1):
                    items.append({
                        "index": idx,
                        "title": n.get("title", f"Defence News Update {idx}"),
                        "description": n.get("description", "")
                    })
                # Add SSB Card if present
                ssb_topic = plan.get("ssb_topic", "SSB Preparation")
                items.append({
                    "index": len(items) + 1,
                    "title": f"SSB Practice - {ssb_topic}",
                    "description": f"Daily SSB practice session: {ssb_topic}. Master your officer like qualities."
                })
        except Exception as e:
            print(f"Warning reading plan: {e}")

    # Fallback to newscard json files if available
    for i in range(1, 5):
        nc_file = os.path.join(BASE_DIR, f"newscard_{i}.json") if i < 4 else os.path.join(BASE_DIR, "ssbcard_4.json")
        if os.path.exists(nc_file) and len(items) < i:
            try:
                with open(nc_file, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    items.append({
                        "index": i,
                        "title": data.get("headline", data.get("title", f"Defence News {i}")),
                        "description": data.get("caption", "")
                    })
            except Exception:
                pass
    return items


def upload_all_reels(privacy="public", news_only=False):
    """Finds all rendered news & SSB reels in output/ and uploads them as YouTube Shorts."""
    metadata_list = get_post_metadata()
    meta_map = {item["index"]: item for item in metadata_list}

    uploaded_count = 0
    # Upload all available news reels dynamically
    max_idx = max((item["index"] for item in metadata_list), default=0)
    for i in range(1, max_idx + 1):
        if news_only and "SSB" in meta_map.get(i, {}).get("title", ""):
            continue
        reel_path = os.path.join(BASE_DIR, "output", f"reel_{i}.mp4")
        if os.path.exists(reel_path):
            meta = meta_map.get(i, {
                "title": f"Daily Defence Update Part {i}",
                "description": "Daily defence and current affairs update."
            })
            print(f"\n{'='*60}\n🚀 Uploading News Reel {i} to YouTube Shorts\n{'='*60}")
            upload_short(
                video_path=reel_path,
                title=meta["title"],
                description=meta["description"],
                privacy_status=privacy
            )
            uploaded_count += 1

    # Also check if combined daily reel exists if no individual reels found
    daily_reel = os.path.join(BASE_DIR, "output", "daily_news_reel.mp4")
    if os.path.exists(daily_reel) and uploaded_count == 0:
        print(f"\n🚀 Uploading daily_news_reel.mp4 to YouTube Shorts")
        upload_short(
            video_path=daily_reel,
            title="Daily AI & Defence News Summary",
            description="Complete summary of today's key updates.\n\n#Shorts #Defence #News",
            privacy_status=privacy
        )
        uploaded_count += 1

    if uploaded_count == 0:
        print("No rendered news reels found in output/ to upload.")
    else:
        print(f"🎉 Successfully uploaded {uploaded_count} News Short(s) to YouTube!")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Upload reels to YouTube Shorts")
    parser.add_argument("--all", action="store_true", help="Upload all reels in output/")
    parser.add_argument("--reel", type=int, help="Upload a specific reel number (e.g. 1, 2, 3, 4)")
    parser.add_argument("--video", type=str, help="Specific video file path")
    parser.add_argument("--title", type=str, default="Daily Defence Update", help="Video title")
    parser.add_argument("--description", type=str, default="", help="Video description")
    parser.add_argument("--privacy", type=str, default="public", choices=["public", "unlisted", "private"])
    args = parser.parse_args()

    if args.video:
        upload_short(args.video, args.title, args.description, privacy_status=args.privacy)
    elif args.reel:
        reel_path = os.path.join(BASE_DIR, "output", f"reel_{args.reel}.mp4")
        meta_list = get_post_metadata()
        meta = next((m for m in meta_list if m["index"] == args.reel), {
            "title": f"Daily Defence Update #{args.reel}",
            "description": "Daily defence update."
        })
        upload_short(reel_path, meta["title"], meta["description"], privacy_status=args.privacy)
    else:
        # Default: upload all available reels
        upload_all_reels(privacy=args.privacy)
