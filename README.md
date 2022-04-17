# shazamctl

```sh
pipx install git+https://codeberg.org/notpushkin/shazamctl
```

## Usage

Recognize music from files:

```
$ shazamctl recognize path/to/rickroll.mp3
At 0:00:10: Never Gonna Give You Up
            by Rick Astley
```

```
$ shazamctl recognize path/to/1h_dnb_mix.mp3 --multiple
At 0:00:16: Higher
            by AKTIVE
            https://song.link/i/1557355435

At 0:03:21: ...
```

Or from microphone:

```
$ shazamctl listen
Listening...
At 0:00:14: Imperium
            by Madeon
            https://song.link/i/955824973
```


## Microphone support on Apple M1

You'll need an x86_64 install of Homebrew.

```sh
arch -x86_64 /usr/local/bin/brew install python@3.10 portaudio
pipx install git+https://codeberg.org/notpushkin/shazamctl --python /usr/local/Cellar/python@3.10/*/bin/python3
pipx runpip shazamctl install pyaudio \
  --global-option='build_ext' \
  --global-option="-I/usr/local/include" \
  --global-option="-L/usr/local/lib"
```

Don't ask.
