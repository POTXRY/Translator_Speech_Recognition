
import torch
import os
import torchaudio
from config import ASR_MODEL_DIR
from transformers import AutoModelForSpeechSeq2Seq, AutoProcessor

class WhisperInference:
    def __init__(self) -> None:
        self.device = 'cuda' if torch.cuda.is_available() else 'cpu'
        self.base_model = 'openai/whisper-medium'
        self.pretrained_model = os.path.join(ASR_MODEL_DIR, 'whisper-medium')
        self.torch_type = torch.float16 if torch.cuda.is_available() else torch.float32

        # Initialize model and processor
        self.model = AutoModelForSpeechSeq2Seq.from_pretrained(
            pretrained_model_name_or_path=self.pretrained_model,
            torch_dtype=self.torch_type,
            device_map="auto"
        ).to(self.device)
        
        self.processor = AutoProcessor.from_pretrained(self.base_model)

    def inference(self, audio_file: str) -> str:
        # Translate Korean speech to English text

        # Load and preprocess audio file
        audio_input, sample_rate = torchaudio.load(audio_file)
        
        # Resample to 16000 Hz if necessary
        if sample_rate != 16000:
            audio_input = torchaudio.transforms.Resample(orig_freq=sample_rate, new_freq=16000)(audio_input)
        
        # Convert stereo to mono
        audio_input = audio_input.mean(dim=0)

        # Prepare inputs for the model
        inputs = self.processor(audio_input, sampling_rate=16000, return_tensors="pt")
        inputs["input_features"] = inputs["input_features"].to(self.device, dtype=self.torch_type)  # Convert to float16
        
        # Configure translation settings
        forced_decoder_ids = self.processor.get_decoder_prompt_ids(language="en", task="translate")
        
        # Generate translation
        generated_tokens = self.model.generate(
            inputs["input_features"],
            forced_decoder_ids=forced_decoder_ids,
            max_new_tokens=200
        )
        
        # Decode the translated text
        translated_text = self.processor.batch_decode(generated_tokens, skip_special_tokens=True)[0]
        return translated_text

# Usage example
if __name__ == "__main__":
    # Initialize the WhisperInference class
    whisper_translator = WhisperInference()
    
    # Path to the audio file
    audio_file = "path_to_your_audio_file.mp3"  # Replace with the actual audio file path
    
    # Translate Korean speech to English text
    translation = whisper_translator.inference(audio_file)
    print("Translated English Text:", translation)
