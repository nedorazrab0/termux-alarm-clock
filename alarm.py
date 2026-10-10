#!/data/data/com.termux/files/usr/bin/env python3
# SPDX-License-Identifier: 0BSD
"""Termux alarm clock."""

from signal import SIG_IGN, SIGINT, signal
from time import sleep, ctime, time
from subprocess import Popen, run
from random import choices
from pathlib import Path
from shlex import join
from os import getpid


class MusicPlayer:
    PLAYER_CMD = "termux-media-player"
    STOP_CMD = [PLAYER_CMD, "stop"]

    def __init__(self) -> None:
        path = Path.home() / "storage" / "downloads"
        self.test_dir = path / "00-termux-alarm-clock"
        self.file = path / "alarm.m4a"

        if not self.file.exists():
            raise FileNotFoundError(f"Place your music file at {self.file}")
        self.test_dir.mkdir(exist_ok=True)

    def stop(self) -> None:
        run(self.STOP_CMD)

    def volume(self, level: int) -> None:
        run(["termux-volume", "music", str(level)])

    def notify(self, text: str) -> None:
        run(["termux-notification-remove", text])
        cmd = [
            "termux-notification",
            "-i", text,
            "-t", text,
            "--on-delete", join(self.STOP_CMD)
        ]
        run(cmd)

    def play(self) -> None:
        # Do not play music if the dir is missing
        if not self.test_dir.is_dir():
            sleep(1)
            return
        self.notify("The volume has changed")
        self.volume(12)
        run([self.PLAYER_CMD, "play", self.file])


# Random KeyboardInterrupt protection
signal(SIGINT, SIG_IGN)
music = MusicPlayer()


def vibrate(duration: float = 1.0) -> float:
    cmd_duration = str(int(duration*1000))
    Popen(["termux-vibrate", "-f", "-d", cmd_duration])
    return duration


def vibrate_random(repeats: int) -> None:
    intervals = (0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.8, 0.9, 1.0)
    random_intervals = choices(intervals, k=repeats)
    for interval in random_intervals:
        duration = vibrate()
        sleep(interval + duration)


def info(minutes: int, seconds: int) -> None:
    run(["termux-dialog", "confirm", "-t", str(minutes)], check=True)
    print("\033[2J\033[H")
    print(f"{minutes} min " * 4)
    print(ctime(time() + seconds))
    print(f"PID: {getpid()}")
    vibrate()


def alarm() -> None:
    print("Wake up")
    vibrate_random(32)
    music.play()
    vibrate_random(32)


def main() -> None:
    minutes = int(input("How many minutes until the alarm "))
    if minutes < 0 or minutes > 550:
        raise ValueError("A misclick?")
    seconds = minutes*60
    run(["termux-wake-lock"], check=True)
    try:
        info(minutes, seconds)
        sleep(seconds)
        alarm()
    finally:
        music.stop()
        run(["termux-wake-unlock"])


if __name__ == "__main__":
    main()
