# functions/audio_processing.py

from pydub import AudioSegment
import os
import hashlib
import json
from datetime import datetime

MP3_FOLDER = "mp3_files"
HASH_FILE = "processed_hashes.json"

# Ensure the MP3 folder exists
os.makedirs(MP3_FOLDER, exist_ok=True)

# Load existing hashes from the JSON file
if os.path.exists(HASH_FILE):
    with open(HASH_FILE, "r") as file:
        HASH_SET = set(json.load(file))
else:
    HASH_SET = set()

def save_hashes():
    """Save the current hashes to the JSON file."""
    with open(HASH_FILE, "w") as file:
        json.dump(list(HASH_SET), file)

def compute_file_hash(file_path: str) -> str:
    """
    Computes the SHA-256 hash of the given file.

    :param file_path: Path to the file
    :return: SHA-256 hash of the file
    """
    hasher = hashlib.sha256()
    with open(file_path, 'rb') as file:
        buf = file.read()
        hasher.update(buf)
    return hasher.hexdigest()

def convert_wav_to_mp3(wav_file_path: str) -> str:
    """
    Converts a WAV file to MP3 and returns the path to the MP3 file.

    :param wav_file_path: Path to the WAV file
    :return: Path to the converted MP3 file
    """
    try:
        file_hash = compute_file_hash(wav_file_path)
        
        if file_hash in HASH_SET:
            raise Exception("Duplicate file detected. The file has already been processed.")

        # Generate a timestamped filename
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        base_filename = os.path.splitext(os.path.basename(wav_file_path))[0]
        mp3_filename = f"{base_filename}_{timestamp}.mp3"
        mp3_file_path = os.path.join(MP3_FOLDER, mp3_filename)
        
        # Convert to MP3
        audio = AudioSegment.from_wav(wav_file_path)
        audio.export(mp3_file_path, format="mp3")
        
        # Store the file hash to prevent future duplicates
        HASH_SET.add(file_hash)
        save_hashes()
        
        # Remove the original WAV file
        os.remove(wav_file_path)
        
        return mp3_file_path
    except Exception as e:
        if os.path.exists(wav_file_path):
            os.remove(wav_file_path)
        raise Exception(f"Failed to convert file: {e}")
