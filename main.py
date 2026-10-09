import time
import subprocess


def check_spotify():
    result = subprocess.run(
        [
            "powershell",
            "-NoProfile",
            "-Command",
            "Get-Process Spotify -ErrorAction SilentlyContinue | "
            "Select-Object Id, MainWindowTitle | ConvertTo-Json"
        ],
        capture_output=True,
        text=True
    )

    if result.returncode != 0 or not result.stdout.strip():
        print("Spotify is not running.")
        return

    print("Spotify process information:")
    print(result.stdout)


def main():
    print("Spotify Ad Controller - Observer")
    print("Press Ctrl+C to stop monitoring.\n")

    try:
        while True:
            check_spotify()
            print("-" * 40)
            time.sleep(3)

    except KeyboardInterrupt:
        print("\nObserver stopped.")


if __name__ == "__main__":
    main()
