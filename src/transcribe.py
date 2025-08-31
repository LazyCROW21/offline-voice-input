import torch
from transformers import pipeline

def transcribe_gujarati_audio(audio_file_path):
    """
    Transcribes a Gujarati audio file using a pre-trained Whisper model,
    prioritizing accuracy over speed.

    Args:
        audio_file_path (str): The path to the audio file to be transcribed.
                               This can be a local file path or a URL.
    """
    try:
        # Determine the device to use (GPU if available, otherwise CPU).
        device = "cuda:0" if torch.cuda.is_available() else "cpu"
        print(f"Using device: {device}")

        # Initialize the transcription pipeline with the specific model.
        # We set generate_kwargs to enable beam search (num_beams > 1),
        # which improves transcription accuracy by exploring more
        # decoding possibilities, but is slower.
        # By not specifying chunk_length_s, the pipeline defaults to
        # processing the entire audio at once, which is best for accuracy.
        transcriber = pipeline(
            task="automatic-speech-recognition",
            model="vasista22/whisper-gujarati-medium",
            device=device,
            generate_kwargs={"num_beams": 5}
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
    
    except ImportError:
        print("Error: Required libraries not found.")
        print("Please install them using: pip install transformers[torch] accelerate")
    except Exception as e:
        print(f"An error occurred during transcription: {e}")

# --- Example Usage ---
if __name__ == "__main__":
    # You can replace this with the path to your own Gujarati audio file.
    # For this example, we'll use a public audio file from Hugging Face Datasets.
    # The file contains a Gujarati phrase.
    # Make sure your system can access this URL.
    sample_audio_url = "C:\\Projects\\offline-voice-input\\temp_voice.wav"
    
    print("This script will download and transcribe a sample Gujarati audio file.")
    print("If you have your own audio file, you can replace the 'sample_audio_url' variable.")
    print(f"Sample audio URL: {sample_audio_url}")
    
    # Run the transcription function with the sample audio.
    transcribe_gujarati_audio(sample_audio_url)
