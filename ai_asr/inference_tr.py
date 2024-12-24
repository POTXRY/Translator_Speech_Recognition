import torch
import os

from config import ASR_MODEL_DIR
from transformers import (
    AutoModelForSpeechSeq2Seq,
    WhisperProcessor,
    pipeline,
)

class WhisperInferencetr:
    def __init__(self) -> None:
        self.device: str = 'cuda:0' if torch.cuda.is_available() else 'cpu'
        self.base_model: str = 'openai/whisper-medium'
        self.pretrained_model: str = os.path.join(ASR_MODEL_DIR, 'whisper-medium')
        self.torch_type: float = torch.float16 if torch.cuda.is_available() else torch.float32
        # if torch.cuda.is_available() else torch.float32
        self.processor = WhisperProcessor.from_pretrained(self.base_model)
        
        self.model = AutoModelForSpeechSeq2Seq.from_pretrained(
            self.base_model,
            torch_dtype=self.torch_type,
            device_map="auto"
        )
        
        self.pipe = pipeline(
            "automatic-speech-recognition",
            model=self.model,
            tokenizer=self.processor.tokenizer,
            feature_extractor=self.processor.feature_extractor,
            torch_dtype=self.torch_type
        )
    
    def inference_tr(
        self,
        audio_file: str,
        lang: str = 'english',
        task: str = 'translate'
    ) -> str:
        '''음성파일 -> 텍스트 추론 수행'''
        options = {
            "language": lang, 
            "task": task,
        }
        result = self.pipe(audio_file, generate_kwargs=options)
        
        if isinstance(result, dict):
            text = result['text']
        elif isinstance(result, list):
            text = ''
            for x in result:
                chunk_list = x['chunks']
                for chunk in chunk_list:
                    text += chunk['text']
        return text