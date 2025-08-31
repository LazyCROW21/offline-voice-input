import torch
from transformers import pipeline

# This script demonstrates how to use the "vasista22/whisper-gujarati-medium" model
# for speech-to-text transcription in Gujarati using the Hugging Face Transformers library.
def transcribe_gujarati_audio(audio_file_path):
    """
    Transcribes a Gujarati audio file using a pre-trained Whisper model,
    prioritizing speed over accuracy.

    Args:
        audio_file_path (str): The path to the audio file to be transcribed.
                               This can be a local file path or a URL.
    """
    try:
        # Determine the device to use (GPU if available, otherwise CPU).
        device = "cuda:0" if torch.cuda.is_available() else "cpu"
        print(f"Using device: {device}")

        # Initialize the transcription pipeline with the specific model.
        # To improve speed, we are no longer using beam search (num_beams > 1),
        # as it is a slower, but more accurate, decoding method. The pipeline
        # now defaults to greedy search, which is much faster.
        # For even more speed, consider using a smaller model like
        # "vasista22/whisper-gujarati-small".
        transcriber = pipeline(
            task="automatic-speech-recognition",
            model="vasista22/whisper-gujarati-small",
            device=device
        )

        # Transcribe the audio file. The pipeline handles all the
        # necessary steps: loading the audio, pre-processing, and running
        # the model.
        print("Transcribing audio... Please wait.")
        transcription_result = transcriber(audio_file_path)

        # The result is a dictionary. We extract the transcribed text.
        transcribed_text = transcription_result["text"]

        print("\n--- Transcription Complete ---")
        print(f"Original Audio: {audio_file_path}")
        print(f"Transcribed Text: {transcribed_text}")
        return transcribed_text
    
    except ImportError:
        print("Error: Required libraries not found.")
        print("Please install them using: pip install transformers[torch] accelerate")
    except Exception as e:
        print(f"An error occurred during transcription: {e}")

# --- Example Usage ---
if __name__ == "__main__":
    # You can replace this with the path to your own local Gujarati audio file.
    # The Hugging Face pipeline can handle various formats, but here we
    # demonstrate with a .wav file.
    sample_audio_path = "C:\\Projects\\offline-voice-input\\temp_voice.wav"
    
    print("This script is configured to transcribe a local .wav file.")
    print("Please replace the 'sample_audio_path' variable with the path to your own file.")
    
    # Run the transcription function with the sample audio path.
    transcribe_gujarati_audio(sample_audio_path)
