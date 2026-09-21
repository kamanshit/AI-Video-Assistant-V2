import whisper


class TranscriptionService:
    def __init__(self):
        self.model = None

    def transcribe(self, audio_path):
        if self.model is None:
            self.model = whisper.load_model("small")

        result = self.model.transcribe(audio_path)
        return result["text"]