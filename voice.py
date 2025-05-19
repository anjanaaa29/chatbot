import sounddevice as sd
from scipy.io.wavfile import write
import whisper
import datetime
import os
import logging

# ==== Logging Configuration ====
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("audio_transcription.log"),
        logging.StreamHandler()
    ]
)

# ==== Load Whisper model once (globally) ====
try:
    logging.info("Loading Whisper model...")
    whisper_model = whisper.load_model("base")  # Try 'tiny' for faster performance
    logging.info("Whisper model loaded successfully.")
except Exception as e:
    logging.critical(f"Error loading Whisper model: {e}")
    whisper_model = None

def record_audio(duration=20, fs=44100, save_dir="recordings"):
    """
    Records audio for a specified duration and saves it as a .wav file.
    Includes exception handling and logging for recording issues.
    """
    try:
        os.makedirs(save_dir, exist_ok=True)
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = os.path.join(save_dir, f"response_{timestamp}.wav")

        logging.info(f"Recording for {duration} seconds...")
        audio = sd.rec(int(duration * fs), samplerate=fs, channels=1)
        sd.wait()
        write(filename, fs, audio)
        logging.info(f"Saved audio to {filename}")
        return filename

    except Exception as e:
        logging.error(f"Error during audio recording: {e}")
        return None

def transcribe_audio(filename):
    """
    Transcribes the audio file using Whisper.
    Includes exception handling and logging for transcription issues.
    """
    try:
        if whisper_model is None:
            raise RuntimeError("Whisper model is not loaded.")

        if not os.path.exists(filename):
            raise FileNotFoundError(f"Audio file not found: {filename}")

        logging.info(f"Transcribing {filename}...")
        result = whisper_model.transcribe(filename)
        text = result["text"].strip()
        logging.info(f"Transcribed text: {text}")
        return text

    except Exception as e:
        logging.error(f"Error during transcription: {e}")
        return ""
