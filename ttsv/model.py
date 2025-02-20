import torch
import torchaudio
import numpy as np
from zonosp.zonos.model import Zonos
from zonosp.zonos.conditioning import make_cond_dict
from zonosp.zonos.utils import DEFAULT_DEVICE as device


class TTSModel:
    """
    A general-purpose TTS base class for Zonos. Loads a pre-trained model
    and creates a speaker embedding from a reference audio file.
    """
    def __init__(
        self,
        model_path: str = "Zyphra/Zonos-v0.1-transformer",
        reference_audio_path: str = "assets/exampleaudio.mp3",
        use_device = device,
        seed: int = 421
    ):
        self.model_path = model_path
        self.use_device = use_device
        self.seed = seed
        
        # Load pre-trained Zonos model
        self.model = Zonos.from_pretrained(self.model_path, device=self.use_device)
        
        # Load reference audio & generate speaker embedding
        wav, sampling_rate = torchaudio.load(reference_audio_path)
        self.speaker = self.model.make_speaker_embedding(wav, sampling_rate)

    def generate_audio(self, text: str, language: str = "en-us") -> np.ndarray:
        """
        Generate TTS audio in-memory as a 1D numpy float32 array.
        """
        torch.manual_seed(self.seed)
        
        # Prepare conditioning
        cond_dict = make_cond_dict(text=text, speaker=self.speaker, language=language)
        conditioning = self.model.prepare_conditioning(cond_dict)

        # Generate codes & decode into audio
        codes = self.model.generate(conditioning)
        wavs = self.model.autoencoder.decode(codes).cpu()

        # Return the first waveform (shape: [num_samples])
        return wavs[0].numpy().astype(np.float32)

    @property
    def sampling_rate(self) -> int:
        """Convenient property to access the model's sampling rate."""
        return self.model.autoencoder.sampling_rate


class ZonosTTS(TTSModel):
    """
    A specialized subclass of TTSModel that mimics your old TTS engine interface.

    - Keeps a `.tts()` method which returns a NumPy waveform.
    - Exposes a `synthesizer.output_sample_rate` property for use in pipelines.
    - Optionally handles multi-speaker logic.
    """
    def __init__(
        self,
        model_path: str = "Zyphra/Zonos-v0.1-transformer",
        reference_audio_path: str = "assets/exampleaudio.mp3",
        language: str = "en-us",
        use_device = device,
        seed: int = 421
    ):
        # Call the base TTSModel initializer
        super().__init__(
            model_path=model_path,
            reference_audio_path=reference_audio_path,
            use_device=use_device,
            seed=seed
        )
        
        # Store language so that .tts() can default to it
        self.language = language
        
        # The pipeline expects tts.synthesizer.output_sample_rate
        class SynthesizerMock:
            def __init__(self, sr: int):
                self.output_sample_rate = sr
        
        self.synthesizer = SynthesizerMock(self.sampling_rate)

    def tts(self, text: str, speaker=None) -> np.ndarray:
        """
        Return a NumPy array of audio samples. 
        'speaker' can be used if your pipeline wants to pass a separate speaker
        embedding, or you can ignore it and use `self.speaker` from the base class.
        """
        # If you want to handle a different speaker embedding, do it here:
        # e.g., if speaker is not None: self.speaker = speaker
        #
        # Then call the base class's generate_audio method:
        return self.generate_audio(text=text, language=self.language)


if __name__ == "__main__":
    # Example usage of the base TTSModel
    base_model = TTSModel(
        model_path="Zyphra/Zonos-v0.1-transformer",
        reference_audio_path="assets/exampleaudio.mp3",
        seed=421
    )
    audio_array = base_model.generate_audio(text="Hello, from TTSModel!")
    print(f"Generated base TTSModel audio shape: {audio_array.shape}")

    # Example usage of the specialized ZonosTTS
    zonos_tts = ZonosTTS(
        model_path="Zyphra/Zonos-v0.1-transformer",
        reference_audio_path="assets/exampleaudio.mp3",
        language="en-us",
        seed=421
    )
    np_audio = zonos_tts.tts("Hello, from ZonosTTS!")
    print(f"Generated specialized ZonosTTS audio shape: {np_audio.shape}")

    # Save an example WAV
    import torchaudio
    import torch

    output_path = "sample.wav"
    audio_tensor = torch.from_numpy(np_audio).unsqueeze(0)  # shape: (1, num_samples)
    torchaudio.save(output_path, audio_tensor, zonos_tts.synthesizer.output_sample_rate)
    print(f"Saved TTS audio to {output_path}")
