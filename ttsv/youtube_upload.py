
import os
import glob
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build, MediaFileUpload
from google.colab import userdata

from ttsv.config import (
    OUTPUT_DIRECTORY,
    FILENAME_TO_PROCESS,
    CHANNEL_TO_UPLOAD,
    CHANNEL_METADATA
)

# Check if running in Google Colab
try:
    from google.colab import userdata
    IN_COLAB = True
    print("Google Colab detected")
except ImportError:
    IN_COLAB = False

if not IN_COLAB:
    print("Not in google Colab")
    from dotenv import load_dotenv
    load_dotenv()

YOUTUBE_SCOPES = [
    "https://www.googleapis.com/auth/youtube.force-ssl",
    "https://www.googleapis.com/auth/youtube.upload",
    "https://www.googleapis.com/auth/youtube.readonly",
    "https://www.googleapis.com/auth/youtubepartner",
    "https://www.googleapis.com/auth/youtube"
]
API_SERVICE_NAME = "youtube"
API_VERSION = "v3"

def get_secret(key:str):
    """Retrieve secrets from the correct environment."""
    if IN_COLAB:
        print(f"fetching key: {key}")
        print(f"fetching key: {userdata.get(key)}")
        print(userdata.get('YOUTUBE_ACCESS_TOKEN_DE'))
        return userdata.get(key)
    return os.getenv(key)

def get_youtube_service(channel_lang):
    """Create YouTube service using credentials for the specified channel."""
    print("get_youtube_service channel launched")
    print(get_secret("YOUTUBE_ACCESS_TOKEN_DE"))
    creds_values = {
    "token": get_secret(f"YOUTUBE_ACCESS_TOKEN_{channel_lang.upper()}"),
    "refresh_token": get_secret(f"YOUTUBE_REFRESH_TOKEN_{channel_lang.upper()}"),
    "client_id": get_secret(f"GOOGLE_CLIENT_ID_{channel_lang.upper()}"),
    "client_secret": get_secret(f"GOOGLE_CLIENT_SECRET_{channel_lang.upper()}")
    }

    # Quick check
    for key, val in creds_values.items():
        if val is None:
            raise ValueError(f"Missing environment variable for {key}")
        print(f"Key:{key},Val:{val}")

    return build(API_SERVICE_NAME, API_VERSION,
        credentials=Credentials(**creds_values, scopes=YOUTUBE_SCOPES)
    )


def upload_video(youtube, file_path, metadata):
    """Upload video to YouTube with channel-specific metadata."""
    request = youtube.videos().insert(
        part="snippet,status",
        body={
            "snippet": {
                "title": metadata["VIDEO_TITLE"],
                "description": metadata["VIDEO_DESCRIPTION"],
                "tags": metadata["VIDEO_TAGS"],
                "categoryId": "22"
            },
            "status": {"privacyStatus": "public"}
        },
        media_body=MediaFileUpload(file_path, chunksize=-1, resumable=True)
    )
    response = request.execute()
    print(f"✅ Uploaded: {response['id']}")
    return response['id']

def upload_subtitles(youtube, video_id, subtitle_files):
    """Upload subtitle files for the video."""
    for sub_path in subtitle_files:
        try:
            lang = os.path.basename(sub_path).split("-")[-1].replace(".sbv", "")
            youtube.captions().insert(
                part="snippet",
                body={
                    "snippet": {
                        "videoId": video_id,
                        "language": lang,
                        "name": f"Subtitles ({lang.upper()})",
                        "isDraft": False
                    }
                },
                media_body=MediaFileUpload(sub_path, mimetype="text/plain")
            ).execute()
            print(f"✅ Added {lang.upper()} subtitles")
        except Exception as e:
            print(f"⚠️ Failed to upload subtitles {sub_path}: {str(e)}")

def process_channel(channel):
    """Handle video and subtitle upload for a single channel."""
    print(f"\n=== Processing {channel.upper()} channel ===")
    
    metadata = CHANNEL_METADATA.get(channel)
    if not metadata:
        print(f"❌ No metadata found for {channel}")
        return

    video_path = os.path.join(
        OUTPUT_DIRECTORY, FILENAME_TO_PROCESS,
        f"{FILENAME_TO_PROCESS}-{channel}.mp4"
    )
    subtitle_files = glob.glob(
        os.path.join(OUTPUT_DIRECTORY, FILENAME_TO_PROCESS,
                    f"{FILENAME_TO_PROCESS}-{channel}-*.sbv")
    )

    if not os.path.exists(video_path):
        print(f"❌ Video file missing: {video_path}")
        return

    youtube = get_youtube_service(channel)
    video_id = upload_video(youtube, video_path, metadata)
    
    if subtitle_files:
        upload_subtitles(youtube, video_id, subtitle_files)
    else:
        print(f"⚠️ No subtitle files found for {channel}")

def upload_video_to_channels():
    """Process all channels in CHANNEL_TO_UPLOAD."""
    for channel in CHANNEL_TO_UPLOAD:
        try:
            process_channel(channel)
        except Exception as e:
            print(f"🔥 Failed to process {channel}: {str(e)}")

if __name__ == "__main__":
    upload_video_to_channels()
