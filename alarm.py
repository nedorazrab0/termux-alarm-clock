#!/data/data/com.termux/files/usr/bin/env python3
# SPDX-License-Identifier: 0BSD
"""Termux alarm clock."""

from signal import SIG_IGN, SIGINT, signal
from time import sleep, ctime, time
from subprocess import Popen, run
from random import choices
from pathlib import Path
from os import getpid


class MusicPlayer:
    PLAYER_CMD = "termux-media-player"

    def __init__(self) -> None:
        path = Path.home() / "storage" / "downloads"
        self.test_dir = path / "00-termux-alarm-clock"
        self.file = path / "alarm.ogg"

        if not self.file.exists():
            raise FileNotFoundError(f"Place your music file at {self.file}")
        # Random KeyboardInterrupt protection
        self.test_dir.mkdir(exist_ok=True)

    def play(self) -> None:
        if not self.test_dir.is_dir():
            return
        text = "The volume has changed"
        run(["termux-notification-remove", text])
        run(["termux-notification", "-c", text, "-i", text])
        sleep(1)
        self.volume(8)
        run([self.PLAYER_CMD, "play", self.file])

    def stop(self) -> None:
        run([self.PLAYER_CMD, "stop"])

    def volume(self, level: int) -> None:
        run(["termux-volume", "music", str(level)])


signal(SIGINT, SIG_IGN)
music = MusicPlayer()


def vibrate(duration: int) -> None:
    Popen(["termux-vibrate", "-f", "-d", str(duration)])


def vibrate_random(repeats: int) -> None:
    durations = choices(range(100, 901, 200), k=repeats)
    for duration in durations:
        vibrate(duration)
        sleep(duration/1000 + 0.2)


def notify(minutes: int, seconds: int) -> None:
    run(["termux-dialog", "confirm", "-t", str(minutes)], check=True)
    print("\033[2J\033[H")
    print(f"{minutes} min " * 4)
    print(ctime(time() + seconds))
    print(f"PID: {getpid()}")
    vibrate(900)


def alarm() -> None:
    print("Wake up")
    vibrate_random(64)
    music.play()
    vibrate_random(64)


def main() -> None:
    minutes = int(input("How many minutes until the alarm "))
    if minutes < 0 or minutes > 540:
        raise ValueError
    seconds = minutes*60
    run(["termux-wake-lock"], check=True)
    try:
        notify(minutes, seconds)
        sleep(seconds)
        alarm()
        music.stop()
    finally:
        run(["termux-wake-unlock"])


if __name__ == "__main__":
    main()
