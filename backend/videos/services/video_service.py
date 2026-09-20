import os
from pathlib import Path
from .transcription_service import TranscriptionService
from .vector_service import VectorService

import yt_dlp
from pydub import AudioSegment
import imageio_ffmpeg


class VideoService:

    def __init__(self, output_dir="media/audio"):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)

        # Get bundled FFmpeg
        self.ffmpeg_path = imageio_ffmpeg.get_ffmpeg_exe()

        # Tell pydub which FFmpeg executable to use
        AudioSegment.converter = self.ffmpeg_path
        AudioSegment.ffmpeg = self.ffmpeg_path
        AudioSegment.ffprobe = self.ffmpeg_path

        self.transcriber = TranscriptionService()
        self.vector_service = VectorService()

    def download_yt_audio(self, url: str) -> str:

        output_path = os.path.join(
            self.output_dir,
            "%(title)s.%(ext)s"
        )

        ydl_opts = {
            "format": "bestaudio/best",
            "outtmpl": output_path,
            "postprocessors": [
                {
                    "key": "FFmpegExtractAudio",
                    "preferredcodec": "wav",
                    "preferredquality": "192",
                }
            ],
            "ffmpeg_location": self.ffmpeg_path,
            "quiet": True,
        }

        with yt_dlp.YoutubeDL(ydl_opts) as ydl:

            info = ydl.extract_info(
                url,
                download=True
            )

            filename = (
                ydl.prepare_filename(info)
                .replace(".webm", ".wav")
                .replace(".m4a", ".wav")
            )

        return filename

    def convert_to_wav(self, input_path: str) -> str:
        """Convert any audio/video file to WAV format."""

        output_path = (
            os.path.splitext(input_path)[0]
            + "_converted.wav"
        )

        audio = AudioSegment.from_file(
            input_path,
            ffmpeg=self.ffmpeg_path
        )

        audio = (
            audio
            .set_channels(1)
            .set_frame_rate(16000)
        )

        audio.export(
            output_path,
            format="wav",
            parameters=["-ar", "16000"]
        )

        return output_path

    def chunk_audio(
        self,
        wav_path: str,
        chunk_minutes: int = 10
    ) -> list:

        audio = AudioSegment.from_wav(wav_path)

        chunk_ms = chunk_minutes * 60 * 1000

        chunks = []

        for i, start in enumerate(
            range(0, len(audio), chunk_ms)
        ):

            chunk = audio[
                start:start + chunk_ms
            ]

            chunk_path = (
                f"{wav_path}_chunk_{i}.wav"
            )

            chunk.export(
                chunk_path,
                format="wav"
            )

            chunks.append(chunk_path)

        return chunks

    def process_input(self, source: str) -> list:

        if (
            source.startswith("http://")
            or source.startswith("https://")
        ):

            print(
                "Detected YouTube URL. "
                "Downloading audio..."
            )

            wav_path = self.download_yt_audio(source)

        else:

            print(
                "Detected local file. "
                "Converting to WAV..."
            )

            wav_path = self.convert_to_wav(source)

        print("Chunking audio...")

        chunks = self.chunk_audio(wav_path)

        print(
            f"Audio ready — "
            f"{len(chunks)} chunk(s) created."
        )

        return chunks

    def transcribe_chunks(self, chunks):
        transcripts = []

        for chunk in chunks:
            text = self.transcriber.transcribe(chunk)
            transcripts.append(text)

        return " ".join(transcripts)

    def process_video(self, video):
        video.status = "processing"
        video.error_message = None
        video.save(update_fields=["status", "error_message"])

        try:
            if video.source:
                source = video.source
            elif video.file:
                source = video.file.path
            else:
                raise ValueError("No video source or file provided.")

            chunks = self.process_input(source)
            transcript = self.transcribe_chunks(chunks)

            video.transcript = transcript
            video.save(update_fields=["transcript"])

            self.vector_service.build_vector_store(
                transcript,
                video.id
            )

            video.status = "completed"
            video.save(update_fields=["status"])

            return video

        except Exception:
            video.status = "failed"
            video.error_message = str(e)
            video.save(update_fields=["status", "error_message"])
            raise