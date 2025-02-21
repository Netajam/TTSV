import json

# Load video_config.json
VIDEO_CONFIG_PATH = "ttsv/video_config.json"
with open(VIDEO_CONFIG_PATH, "r", encoding="utf-8") as file:
    CHANNEL_METADATA = json.load(file)

FILENAME_TO_PROCESS = "PhrasePump5"   
CHANNEL_TO_UPLOAD=["de"]           # e.g. "my_filename"
LANGUAGES_TO_PROCESS = CHANNEL_TO_UPLOAD + ["en"]
REPETITION_PATTERN_TEXT= {"es":{"es": ["", "es", "es", "en", "es"], "en": ["", "es", "es", "en", "es"]},"de":{"de": ["", "de", "en", "en", "de","de",""], "en": ["", "de", "de", "en", "de","","de"]},"ru":{"ru": ["", "ru", "ru", "en", "ru"], "en": ["", "ru", "ru", "en", "ru"]}}
REPETITION_PATTERN_WAVE= [0,0,1,0,1,0,0]

INPUT_DIRECTORY = "text_input"                          # Where your {FILENAME_TO_PROCESS}-{lang}.txt live
OUTPUT_DIRECTORY = "output"  
OUTPUT_DIRECTORY_RAW = "output"              # Where you want WAVs + final merges
MAX_CHARS_PER_LINE = 100                         # If you want chunking, adjust
USE_CHUNKING = False 
LANG_MODEL_MAP = {
    "de": {
        "model_name": "tts_models/de/thorsten/vits",
        "speaker": None  # Single speaker model
    },
    "en": {
        "model_name": "tts_models/en/vctk/vits",
        "speaker": "p301"  #p300 Valid female speaker ID p301 valid male id
    },
    "fr": {
        "model_name": "tts_models/fr/css10/vits", 
        "speaker": None  # Single speaker model
    },
       "es": {
        "model_name": "tts_models/es/css10/vits", 
        "speaker": None  # Single speaker model
    }
}

VIDEO_RESOLUTION = (1280, 720)          # Resolution of the video (width, height)
VIDEO_FPS = 24                           # Frames per second
VIDEO_BACKGROUND_COLOR = (0, 0, 0)       # Background color in RGB (default is black)
VIDEO_CODEC = "libx264"                  # Video codec
AUDIO_CODEC = "aac"                      # Audio codec


YOUTUBE_TITLE = "10 German Sentences with French Translation and subtitles"
YOUTUBE_DESCRIPTION = "Because repetitions lead to progress"
YOUTUBE_CATEGORY_ID = "22"  # See YouTube category list
YOUTUBE_TAGS = ["tag1", "tag2"]
YOUTUBE_PRIVACY_STATUS = "private"  # "public", "private", or "unlisted"

