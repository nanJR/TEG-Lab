"""
Log the Arduino TEG logger's Serial output to a CSV file, and pass your
typed commands (R 4.7, C, N ..., ?) through to the Arduino.

Usage:
    python teg_logger.py --port COM3 --out partA.csv          (Windows)
    python teg_logger.py --port /dev/ttyACM0 --out partB.csv  (Linux/Mac)

Close the Arduino Serial Monitor first: only one program can open the port.
Type a command and press Enter while it runs. Ctrl+C stops logging.
"""
import argparse
import sys
import threading
import time

import serial  # pip install pyserial


def forward_keyboard(port):
    for text in sys.stdin:
        port.write((text.strip() + "\n").encode())


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--port", required=True, help="serial port, e.g. COM3 or /dev/ttyACM0")
    ap.add_argument("--baud", type=int, default=115200)
    ap.add_argument("--out", required=True, help="CSV file to write")
    args = ap.parse_args()

    port = serial.Serial(args.port, args.baud, timeout=1)
    time.sleep(2)  # the Uno resets when the port opens
    threading.Thread(target=forward_keyboard, args=(port,), daemon=True).start()

    rows = 0
    with open(args.out, "w", newline="") as f:
        print(f"Logging to {args.out}. Type commands and press Enter, Ctrl+C to stop.")
        try:
            while True:
                text = port.readline().decode(errors="replace").strip()
                if not text:
                    continue
                f.write(text + "\n")
                f.flush()
                if text.startswith("#") or text.startswith("t_s"):
                    print(text)
                else:
                    rows += 1
                    if rows % 5 == 0:  # echo every 5th sample to keep the screen readable
                        print(text)
        except KeyboardInterrupt:
            pass
    port.close()
    print(f"\nSaved {rows} samples to {args.out}")


if __name__ == "__main__":
    main()
