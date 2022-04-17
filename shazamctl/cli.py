import json
from functools import partial
from logging import getLogger
from pathlib import Path
from typing import Iterable

import typer
from shazamapi import Shazam

from shazamctl.microphone import recognize_microphone

SONG_LINK_TEMPLATE = "https://song.link/i/{0}"

echo_err = partial(typer.echo, err=True)
logger = getLogger(__name__)
app = typer.Typer()


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
):
    print_recognitions(
        recognitions=Shazam().recognize_song(infile),
        multiple=multiple,
    )


@app.command()
def listen(multiple: bool = typer.Option(True)):
    print_recognitions(
        recognitions=recognize_microphone(),
        multiple=multiple,
    )
