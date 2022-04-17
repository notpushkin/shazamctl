from array import array
from typing import Final, Generator, Tuple

from shazamapi import Shazam
from shazamapi.algorithm import SignatureGenerator

try:
    from pyaudio import PyAudio, paInt16  # noqa: WPS433
except ImportError:
    paInt16 = 8  # noqa: N816
    PyAudio = None

ARRAY_TYPE_SIGNED_SHORT: Final = "h"

FORMAT: Final = paInt16  # 2 bytes
CHANNELS: Final = 1
RATE: Final = 16000
RECORD_SECONDS: Final = 3
CHUNK: Final = 1024


def recognize_microphone() -> Generator[Tuple[int, dict], None, None]:
    if PyAudio is None:
        raise RuntimeError("PyAudio is not installed")

    stream = PyAudio().open(
        format=FORMAT,
        channels=CHANNELS,
        rate=RATE,
        input=True,
        frames_per_buffer=CHUNK,
    )
    signature_generator = SignatureGenerator()
    signature_generator.MAX_TIME_SECONDS = RECORD_SECONDS

    while True:  # noqa: WPS457
        for _ in range(int(RATE / CHUNK * RECORD_SECONDS)):
            data = array(ARRAY_TYPE_SIGNED_SHORT)
            data.frombytes(stream.read(CHUNK))
            signature_generator.feed_input(data)

        stream.stop_stream()

        for signature in signature_generator:
            results = Shazam().send_recognize_request(signature)
            current_offset = int(
                signature_generator.samples_processed // RATE,
            )
            yield current_offset, results

        stream.start_stream()
