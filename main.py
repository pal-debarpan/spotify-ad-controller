import os
import re
import subprocess
import time
from pathlib import Path

PROJECT_DIR = Path(__file__).resolve().parent
DETECTOR_SCRIPT = PROJECT_DIR / "inspect_spotify.ps1"

CHECK_INTERVAL = 3
RESTART_COOLDOWN = 120



def detect_ad():
    """Check Spotify's accessible UI for an active advertisement."""
    try:
        result = subprocess.run(
            [
                "powershell",
                "-NoProfile",
                "-ExecutionPolicy",
                "Bypass",
                "-File",
                str(DETECTOR_SCRIPT),
            ],
            capture_output=True,
            text=True,
            timeout=15,
        )

        output = result.stdout + result.stderr

        if result.returncode != 0:
            print("Detector encountered an error.")
            return False

        # A normal track is playing, so this isn't an ad.
        if re.search(r"Now playing:", output, re.IGNORECASE):
            return False

        # Look for the specific labels seen during an actual ad.
        return bool(
            re.search(
                r"Spotify\s*[–—-]\s*Advertisement|Advertisement\s*•",
                output,
                re.IGNORECASE,
            )
        )

    except subprocess.TimeoutExpired:
        print("Detector timed out.")
        return False


def restart_spotify():
    """Close Spotify and launch it again."""
    print("\nAdvertisement detected!")
    print("Closing Spotify...")

    subprocess.run(
        [
            "powershell",
            "-NoProfile",
            "-Command",
            "Get-Process Spotify -ErrorAction SilentlyContinue "
            "| Stop-Process -Force",
        ],
        capture_output=True,
        text=True,
    )

    time.sleep(2)

    print("Reopening Spotify...")

    try:
        os.startfile("spotify:")
        print("Spotify launch requested.")
        print("Waiting 10 seconds for Spotify to settle...")
        time.sleep(10)
        return True
    except OSError as error:
        print(f"Could not reopen Spotify: {error}")
        return False


def main():
    if not DETECTOR_SCRIPT.exists():
        print(f"Detector script not found: {DETECTOR_SCRIPT}")
        return

    print("Spotify Ad Controller started.")
    print(f"Checking every {CHECK_INTERVAL} seconds.")
    print("Press Ctrl+C to stop.\n")

    last_restart = 0.0
    previous_ad_state = False

    try:
        while True:
            ad_detected = detect_ad()

            if ad_detected and not previous_ad_state:
                now = time.monotonic()

                if now - last_restart >= RESTART_COOLDOWN:
                    if restart_spotify():
                        last_restart = time.monotonic()
                else:
                    print("Advertisement detected; restart cooldown active.")

            elif ad_detected:
                print("Advertisement still detected.")

            else:
                print("No advertisement detected.")

            previous_ad_state = ad_detected
            time.sleep(CHECK_INTERVAL)

    except KeyboardInterrupt:
        print("\nSpotify Ad Controller stopped.")


if __name__ == "__main__":
    main()