import os
import numpy as np
from scipy.io.wavfile import read as read_wav, write as write_wav
from dotenv import load_dotenv
from config import (
    CHANNEL_TO_UPLOAD,
    OUTPUT_DIRECTORY,
    FILENAME_TO_PROCESS,
    REPETITION_PATTERN_WAVE,
    REPETITION_PATTERN_TEXT,
)
from utils import format_timestamp, parse_generated_filename

# Load environment variables
load_dotenv()

def gather_files(channel_lang):
    """
    Gather WAV and TXT files for a given channel language.
    Returns a dictionary mapping line numbers to file info.
    """
    file_map = {}
    for lang in [channel_lang, "en"]:
        speech_dir = os.path.join(OUTPUT_DIRECTORY, FILENAME_TO_PROCESS, lang, "speech")
        text_dir = os.path.join(OUTPUT_DIRECTORY, FILENAME_TO_PROCESS, lang, "text")
        if not os.path.isdir(speech_dir):
            print(f"WARNING: Speech directory not found for language '{lang}' at '{speech_dir}'. Skipping.")
            continue

        for fname in os.listdir(speech_dir):
            if not fname.lower().endswith(".wav"):
                continue

            parsed = parse_generated_filename(fname)
            if not parsed or parsed[1] != lang:
                continue

            line_num, _, duration_ms = parsed
            wav_path = os.path.join(speech_dir, fname)
            txt_path = os.path.join(text_dir, os.path.splitext(fname)[0] + ".txt")
            file_map[(line_num, lang)] = {
                "wav_path": wav_path,
                "txt_path": txt_path,
                "duration_ms": duration_ms
            }
    return file_map

def merge_wav_files(file_map, channel_lang, max_line_num):
    """
    Merge WAV files for a given channel language and English.
    Returns merged audio, sample rate, and timestamps (grouped by line).
    """
    merged_audio, sample_rate = None, None
    timestamps = []  # List of lists: [[(start1, end1), ...], ...]
    elapsed_time_sec = 0.0

    for line_num in range(1, max_line_num + 1):
        line_timestamps = []
        for wave_entry in REPETITION_PATTERN_WAVE:
            lang = channel_lang if wave_entry == 0 else "en"
            info = file_map.get((line_num, lang))
            if not info:
                continue

            # Read WAV file
            sr, audio_data = read_wav(info["wav_path"])
            if audio_data.dtype == np.int16:
                audio_data = audio_data.astype(np.float32) / 32767.0

            if sample_rate is None:
                sample_rate = sr
            elif sr != sample_rate:
                continue

            merged_audio = audio_data if merged_audio is None else np.concatenate([merged_audio, audio_data])

            # Record timestamps (in seconds as floats)
            start_ts = elapsed_time_sec
            end_ts = start_ts + info["duration_ms"] / 1000.0
            line_timestamps.append((start_ts, end_ts))
            elapsed_time_sec = end_ts

        # Format timestamps for this line
        formatted_line_timestamps = [
            (format_timestamp(start), format_timestamp(end))
            for start, end in line_timestamps
        ]
        timestamps.append(formatted_line_timestamps)

    return merged_audio, sample_rate, timestamps

def create_subtitles(file_map, channel_lang, max_line_num, timestamps):
    """
    Create subtitle files for a given channel language.
    Returns a dictionary of subtitle text for each language.
    """
    subtitles = {lang: [] for lang in REPETITION_PATTERN_TEXT[channel_lang].keys()}

    for line_num in range(1, max_line_num + 1):
        line_index = line_num - 1  # Convert to 0-based index
        line_timestamps = timestamps[line_index]

        # Get the repetition pattern for this line (e.g., ["", "es", "es", "en", "es"])
        for lang, pattern in REPETITION_PATTERN_TEXT[channel_lang].items():
            for i in range(len(REPETITION_PATTERN_WAVE)):
                if i >= len(line_timestamps):
                    continue  # Skip if no timestamp for this pattern index
                start_ts, end_ts = line_timestamps[i]
                text_lang = pattern[i]

                if text_lang == "":
                    # Add timestamp followed by a blank line
                    subtitles[lang].append(f"{start_ts},{end_ts}\n\n")
                else:
                    info = file_map.get((line_num, text_lang))
                    if info and os.path.isfile(info["txt_path"]):
                        with open(info["txt_path"], "r", encoding="utf-8") as tf:
                            # Add timestamp, text, and blank line
                            subtitles[lang].append(f"{start_ts},{end_ts}\n{tf.read().strip()}\n\n")
                    else:
                        # Add timestamp with empty text and blank line
                        subtitles[lang].append(f"{start_ts},{end_ts}\n\n")

    return subtitles
def generate_sbv_files(channel_lang, subtitle_langs):
    """
    Create .sbv copies of subtitle .txt files for a channel.
    """
    for lang in subtitle_langs:
        txt_path = os.path.join(
            OUTPUT_DIRECTORY, FILENAME_TO_PROCESS,
            f"{FILENAME_TO_PROCESS}-{channel_lang}-{lang}.txt"
        )
        sbv_path = txt_path.replace(".txt", ".sbv")
        
        if os.path.exists(txt_path):
            try:
                with open(txt_path, "r", encoding="utf-8") as src:
                    with open(sbv_path, "w", encoding="utf-8") as dest:
                        dest.write(src.read())
                print(f"  SBV file created: {sbv_path}")
            except Exception as e:
                print(f"ERROR: Failed to create SBV file {sbv_path}: {e}")
        else:
            print(f"WARNING: Source TXT file not found for SBV generation: {txt_path}")

def save_outputs(channel_lang, merged_audio, sample_rate, subtitles):
    """
    Save merged WAV and subtitle files for a given channel language.
    """
    # Save merged WAV
    merged_wav_output = os.path.join(OUTPUT_DIRECTORY, FILENAME_TO_PROCESS, f"{FILENAME_TO_PROCESS}-{channel_lang}-merged.wav")
    if merged_audio is not None and sample_rate is not None:
        write_wav(merged_wav_output, sample_rate, (merged_audio * 32767).astype(np.int16))
        print(f"  Merged audio saved to: {merged_wav_output}")

    # Save subtitles
    for lang, text in subtitles.items():
        subtitle_path = os.path.join(OUTPUT_DIRECTORY, FILENAME_TO_PROCESS, f"{FILENAME_TO_PROCESS}-{channel_lang}-{lang}.txt")
        with open(subtitle_path, "w", encoding="utf-8") as f:
            f.write("".join(text))
        print(f"  Subtitles saved to: {subtitle_path}")
    generate_sbv_files(channel_lang, subtitles.keys())


def process_channel(channel_lang):
    """
    Process a single channel: merge WAV files and create subtitles.
    """
    file_map = gather_files(channel_lang)
    max_line_num = max((k[0] for k in file_map.keys()), default=0)
    if max_line_num == 0:
        print(f"ERROR: No valid audio files found for channel '{channel_lang}'.")
        return

    merged_audio, sample_rate, timestamps = merge_wav_files(file_map, channel_lang, max_line_num)
    subtitles = create_subtitles(file_map, channel_lang, max_line_num, timestamps)
    save_outputs(channel_lang, merged_audio, sample_rate, subtitles)

def create_merge_files():
    """
    Process all channels in CHANNEL_TO_UPLOAD.
    """
    for channel_lang in CHANNEL_TO_UPLOAD:
        print(f"Processing channel: {channel_lang}")
        process_channel(channel_lang)
    print("Merging complete!")

if __name__ == "__main__":
    create_merge_files()