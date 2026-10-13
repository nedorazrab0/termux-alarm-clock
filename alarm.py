#!/data/data/com.termux/files/usr/bin/env python3
# SPDX-License-Identifier: 0BSD
"""Termux alarm clock."""

from time import localtime, strftime, sleep, time
from signal import SIG_IGN, SIGINT, signal
from subprocess import Popen, run
from random import choices
from pathlib import Path
from shlex import join


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
        sleep(1)
        # Remove the dir to prevent the music playing
        if not self.test_dir.is_dir():
            return
        self.notify("The volume has changed")
        self.volume(12)
        run([self.PLAYER_CMD, "play", self.file])


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


def alarm(music: MusicPlayer) -> None:
    print("Wake up")
    vibrate_random(64)
    music.play()
    vibrate_random(32)


def dialog() -> int:
    min_cycle = 6000
    max_cycle = 33001
    cycle = 5400

    now = time()
    variants = tuple(
        (
            strftime("%H:%M %d %h", localtime(now + cycle_seconds)),
            cycle_seconds
        )
        for cycle_seconds in range(min_cycle, max_cycle, cycle)
    )
    for number, (label, _) in enumerate(variants):
        print(f"{number}  {label}")
    answer = int(input("Enter a number: "))
    if answer < 0:
        raise ValueError
    label, seconds = variants[answer]
    print("\033[H\033[J")
    print(label)
    return seconds


def main() -> None:
    # Random KeyboardInterrupt protection
    signal(SIGINT, SIG_IGN)

    music = MusicPlayer()
    seconds = dialog()
    run(["termux-wake-lock"], check=True)
    try:
        vibrate()
        sleep(seconds)
        alarm(music)
        music.stop()
    finally:
        run(["termux-wake-unlock"])


if __name__ == "__main__":
    main()
