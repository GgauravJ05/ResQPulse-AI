import io
import math
import numpy as np
from faster_whisper import WhisperModel
from pydub import AudioSegment
from pydub.exceptions import CouldntDecodeError
from src.api.schemas import TranscribeResult

print("Loading faster-whisper (small.en, int8)...")
whisper_model = WhisperModel("small.en", device="cpu", compute_type="int8")

def transcribe_bytes(audio_bytes: bytes) -> TranscribeResult:
    """Processes audio entirely in RAM for minimum latency."""
    try:
        # Load audio directly from memory buffer
        audio = AudioSegment.from_file(io.BytesIO(audio_bytes))
    except CouldntDecodeError:
        raise ValueError("Could not decode audio file.")
    
    duration_s = len(audio) / 1000.0
    if duration_s > 60.0:
        raise ValueError("Audio exceeds 60 seconds limit.")
        
    # Convert to 16kHz mono directly in memory
    audio = audio.set_frame_rate(16000).set_channels(1)
    
    # Convert pydub audio to a float32 NumPy array required by Whisper
    samples = np.array(audio.get_array_of_samples()).astype(np.float32) / 32768.0
    
    # Transcribe directly from the NumPy array
    segments_gen, info = whisper_model.transcribe(
        samples, 
        vad_filter=True,
        vad_parameters=dict(min_silence_duration_ms=500)
    )
    
    segments = list(segments_gen)
    
    if not segments:
        return TranscribeResult(
            transcript="", confidence=0.0, low_confidence=True, duration_s=duration_s
        )
        
    full_text = " ".join([seg.text.strip() for seg in segments])
    
    exp_logprobs = [math.exp(seg.avg_logprob) for seg in segments]
    confidence = sum(exp_logprobs) / len(exp_logprobs)
    max_no_speech = max([seg.no_speech_prob for seg in segments])
    low_confidence = bool(confidence < 0.5 or max_no_speech > 0.6)
    
    return TranscribeResult(
        transcript=full_text,
        confidence=round(confidence, 4),
        low_confidence=low_confidence,
        duration_s=round(duration_s, 2)
    )