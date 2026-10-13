#!/data/data/com.termux/files/usr/bin/env python3
# SPDX-License-Identifier: 0BSD
"""Termux alarm clock."""

from time import localtime, strftime, sleep, time
from subprocess import check_output, Popen, run
from signal import SIG_IGN, SIGINT, signal
from random import choices
from pathlib import Path
from shlex import join
from json import loads


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
        # Remove the dir to prevent the music playing
        if not self.test_dir.is_dir():
            sleep(1)
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
    now = time()
    variants = tuple(
        (
            strftime("%H:%M %d %h", localtime(now + cycle_seconds + 600)),
            cycle_seconds
        )
        for cycle_seconds in range(6000, 33001, 5400)
    )
    number = 0
    for variant in variants:
        number += 1
        print(f"{number}) {variant[0]}")
    answer = int(input("How many cycles: ")) - 1
    result = variants[answer][1]
    print("\033[H\033[J", result)
    return result


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
