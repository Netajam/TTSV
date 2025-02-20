import os
import numpy as np
from typing import Union, List
from scipy.io.wavfile import write as write_wav
from ttsv.model import ZonosTTS
from ttsv.config import (
    LANGUAGES_TO_PROCESS,
    OUTPUT_DIRECTORY,
    FILENAME_TO_PROCESS,
    INPUT_DIRECTORY,
    USE_CHUNKING,
    MAX_CHARS_PER_LINE, 
)

def clean_line(line: str, forbidden_chars: Union[None, List[str]] = None) -> str:
    """
    Clean a single line of text by removing unwanted characters and stripping whitespace.
    """
    if forbidden_chars is None:
        forbidden_chars = ["*", "#"]
    translation_table = str.maketrans('', '', ''.join(forbidden_chars))
    return line.strip().translate(translation_table)


def process_input_texts(
    input_dir=INPUT_DIRECTORY, 
    filename=FILENAME_TO_PROCESS,
    output_dir=OUTPUT_DIRECTORY,
    model=None 
):
    """
    For each language in LANGUAGES_TO_PROCESS, find {folder}/{filename}-{lang}.txt,
    read line by line, generate wav+txt, and save in OUTPUT_DIRECTORY/{filename}/{lang}/speech + text.
    Supports multi-speaker models through configuration of the TTS object.
    """
    if model is None:
        raise ValueError("No TTS model (tts) provided to process_input_texts.")

    for lang in LANGUAGES_TO_PROCESS:
        input_txt = os.path.join(input_dir, f"{filename}-{lang}.txt")
        if not os.path.isfile(input_txt):
            print(f"WARNING: Input file not found for {lang} -> {input_txt}")
            continue

        # Create output directories
        speech_dir = os.path.join(output_dir, filename, lang, "speech")
        text_dir = os.path.join(output_dir, filename, lang, "text")
        os.makedirs(speech_dir, exist_ok=True)
        os.makedirs(text_dir, exist_ok=True)


        with open(input_txt, "r", encoding="utf-8") as f:
            for line_num, line in enumerate(f, start=1):
                cleaned_line = clean_line(line)
                if not cleaned_line:
                    continue  # Skip empty lines

                try:
                    # Possibly chunk up long lines
                    if USE_CHUNKING and len(cleaned_line) > MAX_CHARS_PER_LINE:
                        chunks = [
                            cleaned_line[i : i + MAX_CHARS_PER_LINE]
                            for i in range(0, len(cleaned_line), MAX_CHARS_PER_LINE)
                        ]
                        
                        audio_all = []
                        for chunk in chunks:
                            if hasattr(model, 'speaker') and model.speaker is not None:
                                audio_chunk = model.tts(text=chunk, speaker=model.speaker)
                            else:
                                audio_chunk = model.tts(text=chunk)

                            audio_chunk = np.array(audio_chunk, dtype=np.float32)
                            audio_all.append(audio_chunk)
                        
                        audio = np.concatenate(audio_all) if audio_all else np.array([], dtype=np.float32)
                    
                    else:
                        # Single chunk
                        if hasattr(model, 'speaker') and model.speaker is not None:
                            audio = model.tts(text=cleaned_line, speaker=model.speaker)
                        else:
                            audio = model.tts(text=cleaned_line)

                        audio = np.array(audio, dtype=np.float32)

                    # Audio metadata
                    sample_rate = model.synthesizer.output_sample_rate
                    duration_ms = int((len(audio) / sample_rate) * 1000)

                    # Filenames
                    base_name = f"{line_num}-{lang}-{duration_ms}"
                    wav_path = os.path.join(speech_dir, f"{base_name}.wav")
                    txt_path = os.path.join(text_dir, f"{base_name}.txt")

                    # Save the WAV file
                    write_wav(wav_path, sample_rate, (audio * 32767).astype(np.int16))

                    # Save the cleaned text
                    with open(txt_path, "w", encoding="utf-8") as out_f:
                        out_f.write(cleaned_line)

                except Exception as e:
                    print(f"Error processing line {line_num} ({lang}): {str(e)}")
                    continue

        print(f"Completed TTS for '{lang}': {line_num} lines processed")


if __name__ == "__main__":
    # Create your ZonosTTS instance with desired paths
    zonos_tts = ZonosTTS(
        model_path="Zyphra/Zonos-v0.1-transformer", 
        reference_audio_path="assets/exampleaudio.mp3",
        language="en-us"  # or dynamically set this per language
    )
    
    # Now just call your processing function with the TTS object
    process_input_texts(
        model=zonos_tts
    )
