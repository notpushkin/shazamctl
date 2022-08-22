import json
import logging
from functools import partial
from pathlib import Path
from types import MappingProxyType
from typing import Final, Iterable
import webbrowser

import typer
from shazamapi import Shazam

from shazamctl.microphone import recognize_microphone

SONG_LINK_TEMPLATE: Final = "https://song.link/i/{0}"
VERBOSITY_COUNT_TO_LEVEL: Final = MappingProxyType({
    0: logging.ERROR,
    1: logging.WARNING,
    2: logging.INFO,
    3: logging.DEBUG,
})

echo_err = partial(typer.echo, err=True)
logger = logging.getLogger(__name__)
app = typer.Typer()


@app.callback()
def main(verbose: int = typer.Option(0, "-v", count=True)):
    """
    A toy command-line client for Shazam.
    """
    logging.basicConfig(
        level=VERBOSITY_COUNT_TO_LEVEL.get(verbose, logging.DEBUG),
    )


def format_offset(seconds: int):
    minutes, seconds = divmod(seconds, 60)
    hours, minutes = divmod(minutes, 60)
    return "{h}:{m:0>2}:{s:0>2}".format(
        h=hours,
        m=minutes,
        s=seconds,
    )


def print_recognitions(
    recognitions: Iterable[dict],
    multiple: bool = False,
    open: bool = False,
):
    prev_track_key = None
    for (offset, resp) in recognitions:
        logger.debug(
            "At {offset}: {resp}".format(
                offset=format_offset(offset),
                resp=json.dumps(resp, indent=4),
            ),
        )

        track = resp.get("track")
        if track is None:
            continue

        next_track_key = track.get("key")
        if prev_track_key and next_track_key == prev_track_key:
            continue

        actions: list = track.get("hub", {}).get("actions", [])
        apple_music_id = next(
            (
                action.get("id")
                for action in actions
                if action.get("type") == "applemusicplay"
            ),
            None,
        )

        typer.echo(
            "\n            ".join((
                "At {offset}: {title}".format(
                    offset=format_offset(offset),
                    title=track.get("title", "Unknown track"),
                ),
                "by {artist}".format(
                    artist=track.get("subtitle", "Unknown artist"),
                ),
                *(
                    [] if apple_music_id is None
                    else [SONG_LINK_TEMPLATE.format(apple_music_id)]
                ),
                "",
            )),
        )
        if open and apple_music_id is not None:
            webbrowser.open(SONG_LINK_TEMPLATE.format(apple_music_id))

        prev_track_key = next_track_key
        if not multiple:
            break


@app.command()
def recognize(
    infile: Path,
    multiple: bool = typer.Option(
        default=False,
        help="Don't stop after recognizing one track",
    ),
    no_open: bool = typer.Option(
        None,
        "--no-open /",
        help="Do not open song page after recognition (default if --multiple specified)",
    ),
):
    if no_open is None:
        no_open = multiple

    print_recognitions(
        recognitions=Shazam().recognize_song(infile),
        multiple=multiple,
        open=not no_open,
    )


@app.command()
def listen(
    multiple: bool = typer.Option(
        default=False,
        help="Don't stop after recognizing one track",
    ),
    no_open: bool = typer.Option(
        None,
        "--no-open /",
        help="Do not open song page after recognition (default if --multiple specified)",
    ),
):
    if no_open is None:
        no_open = multiple

    echo_err("Listening...")
    print_recognitions(
        recognitions=recognize_microphone(),
        multiple=multiple,
        open=not no_open,
    )
