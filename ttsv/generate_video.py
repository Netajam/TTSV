import os
import subprocess
from ttsv.config import (
    FILENAME_TO_PROCESS,
    OUTPUT_DIRECTORY,
    CHANNEL_TO_UPLOAD,
    VIDEO_RESOLUTION,
    VIDEO_FPS,
    VIDEO_BACKGROUND_COLOR,
    VIDEO_CODEC,
    AUDIO_CODEC,
)

def create_black_videos_with_audio():
    """
    Creates black background videos with merged audio for each channel in CHANNEL_TO_UPLOAD.
    """
    for channel in CHANNEL_TO_UPLOAD:
        # Paths for this channel
        merged_audio_path = os.path.join(
            OUTPUT_DIRECTORY, FILENAME_TO_PROCESS, 
            f"{FILENAME_TO_PROCESS}-{channel}-merged.wav"
        )
        merged_video_path = os.path.join(
            OUTPUT_DIRECTORY, FILENAME_TO_PROCESS, 
            f"{FILENAME_TO_PROCESS}-{channel}.mp4"  # ✅ Clean name (e.g., "Pizza-es.mp4")
        )
        if not os.path.isfile(merged_audio_path):
            print(f"ERROR: Merged audio file for channel '{channel}' not found at '{merged_audio_path}'. Skipping.")
            continue

        try:
            # Convert background color tuple to ffmpeg hex format (e.g., black = 0x000000)
            color_r, color_g, color_b = VIDEO_BACKGROUND_COLOR
            color_hex = "0x{:02x}{:02x}{:02x}".format(color_r, color_g, color_b)
            resolution = f"{VIDEO_RESOLUTION[0]}x{VIDEO_RESOLUTION[1]}"

            # Build ffmpeg command (no subtitles)
            ffmpeg_cmd = [
                'ffmpeg',
                '-y',  # Overwrite output
                '-f', 'lavfi',
                '-i', f'color=c={color_hex}:s={resolution}:r={VIDEO_FPS}',  # Black background
                '-i', merged_audio_path,  # Audio input
                '-shortest',  # End when audio ends
                '-c:v', VIDEO_CODEC,
                '-c:a', AUDIO_CODEC,
                '-vf', 'format=yuv420p',  # Ensure compatibility
                merged_video_path
            ]

            print(f"Creating video for channel '{channel}'...")
            subprocess.run(ffmpeg_cmd, check=True)
            print(f"Successfully created video: '{merged_video_path}'")

        except subprocess.CalledProcessError as e:
            print(f"ffmpeg command failed for channel '{channel}': {e}")
        except Exception as e:
            print(f"Unexpected error for channel '{channel}': {e}")

if __name__ == "__main__":
    create_black_videos_with_audio()