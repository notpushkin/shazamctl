import json
from functools import partial
from logging import getLogger
from pathlib import Path

import typer
from shazamapi import Shazam

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


@app.command()
def recognize(
    infile: Path,
    multiple: bool = typer.Option(
        default=False,
        help="Don't stop after recognizing one track",
    ),
):
    prev_track_key = None
    for (offset, resp) in Shazam().recognize_song(infile):
        track = resp.get("track")
        if track is None:
            logger.info(
                "At {offset}: {resp}".format(
                    offset=format_offset(offset),
                    resp=json.dumps(resp, indent=4),
                ),
            )
            continue

        next_track_key = track.get("key")
        if prev_track_key and next_track_key == prev_track_key:
            continue

        typer.echo(
            "At {offset}: {title} by {artist}".format(
                offset=format_offset(offset),
                title=track.get("title", "Unknown track"),
                artist=track.get("subtitle", "Unknown artist"),
            ),
        )

        prev_track_key = next_track_key
        if not multiple:
            break


@app.command()
def listen(multiple: bool = typer.Option(True)):
    echo_err("Not implemented... yet")
