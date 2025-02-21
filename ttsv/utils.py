import os
import re
import torch
import numpy as np
from scipy.io.wavfile import write as write_wav, read as read_wav
from ttsv.config import LANGUAGES_TO_PROCESS, OUTPUT_DIRECTORY, FILENAME_TO_PROCESS, \
                  LANG_MODEL_MAP, ROOT_DIRECTORY, USE_CHUNKING, MAX_CHARS_PER_LINE

device = "cuda" if torch.cuda.is_available() else "cpu"
_tts_objects = {}  # Stores TTS instances with speaker configurations



def format_timestamp(total_seconds):
    """
    Convert a floating-point number of seconds to H:MM:SS.mmm format.
    Example: 0 -> '0:00:00.000'
    """
    hours = int(total_seconds // 3600)
    minutes = int((total_seconds % 3600) // 60)
    seconds = int(total_seconds % 60)
    milliseconds = int((total_seconds - int(total_seconds)) * 1000)
    return f"{hours}:{minutes:02}:{seconds:02}.{milliseconds:03}"

def parse_generated_filename(file_name):
    """
    Parse a filename of the form '{lineNum}-{lang}-{duration}.ext'
    e.g. '10-fr-1234.wav' or '10-fr-1234.txt'
    Returns (line_num, lang, duration_in_ms) as integers/strings.
    If it doesn't match, returns None.
    """
    base = os.path.splitext(os.path.basename(file_name))[0]  # e.g. '10-fr-1234'
    match = re.match(r'^(\d+)-([a-zA-Z]+)-(\d+)$', base)
    if not match:
        return None
    line_num_str, lang_str, dur_str = match.groups()
    try:
        line_num = int(line_num_str)
        duration_ms = int(dur_str)
        return (line_num, lang_str, duration_ms)
    except ValueError:
        return None