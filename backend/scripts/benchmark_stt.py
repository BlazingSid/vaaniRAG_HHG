import asyncio
import statistics
import time
import os
from pathlib import Path
from dotenv import load_dotenv

PROJECT_ROOT = Path(__file__).resolve().parents[2] 

load_dotenv(PROJECT_ROOT / ".env")
from pathlib import Path

from app.config import get_settings
from app.sarvam import SarvamSpeechClient




async def main():
    settings = get_settings()
    client = SarvamSpeechClient(settings)

    project_root = Path(__file__).resolve().parents[2]
    audio_path = project_root / "test.wav"

    audio = audio_path.read_bytes()

    print(f"Audio: {audio_path}")
    print(f"Audio size: {len(audio) / 1024:.1f} KB")
    print("\nRunning 5 direct Sarvam STT tests...\n")

    times = []

    try:
        for i in range(5):
            started = time.perf_counter()

            result = await client.transcribe(
                audio,
                filename="test.wav",
                content_type="audio/wav",
                language="mr-IN",
            )

            elapsed = (time.perf_counter() - started) * 1000
            times.append(elapsed)

            print(
                f"Test {i + 1}: "
                f"{elapsed:.2f} ms | "
                f"{result.text}"
            )

    finally:
        await client.client.aclose()

    print("\n--- Results ---")
    print(f"Min:     {min(times):.2f} ms")
    print(f"Max:     {max(times):.2f} ms")
    print(f"Average: {statistics.mean(times):.2f} ms")
    print(f"Median:  {statistics.median(times):.2f} ms")


if __name__ == "__main__":
    asyncio.run(main())