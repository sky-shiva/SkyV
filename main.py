"""VoiceBud: hold ctrl+shift to dictate anywhere. Fully offline."""
import threading
import time

import yaml

import inject
from audio import Recorder
from cleanup import Cleaner
from hotkey import PushToTalk
from transcribe import Transcriber
from overlay import Overlay

APP_NAME = "VoiceBud"


def main():
    with open("config.yaml") as f:
        cfg = yaml.safe_load(f)

    print(f"Loading STT model ({cfg['stt']['model']})...")
    stt = Transcriber(cfg["stt"])
    cleaner = Cleaner(cfg["llm"])
    rec = Recorder(
        sample_rate=cfg["audio"]["sample_rate"],
        channels=cfg["audio"]["channels"],
        preroll_ms=cfg["audio"]["preroll_ms"],
    )
    rec.start_stream()
    
    overlay = Overlay(lambda: rec.level, name="Sky")

    def on_press():
        rec.start()
        overlay.show()

    def process(audio):
        t0 = time.time()
        raw = stt.transcribe(audio)
        if not raw:
            print("(no speech detected)")
            return
        text = cleaner.clean(raw)
        inject.inject(text, cfg["inject"])
        print(f'→ "{text}"  ({time.time() - t0:.2f}s)')

    def on_release():
        overlay.hide()  # Hide immediately
        audio = rec.stop()
        threading.Thread(target=process, args=(audio,), daemon=True).start()

    key = cfg["hotkey"]["key"]
    mode = cfg["hotkey"].get("mode", "hold")
    PushToTalk(key, on_press, on_release, mode=mode).start()
    action = "Press" if mode == "toggle" else "Hold"
    print(f"{APP_NAME} ready. {action} [{key}] to dictate ({mode} mode).")
    
    try:
        while True:
            time.sleep(0.1)
    except KeyboardInterrupt:
        print("Shutting down...")
        overlay.hide()
        rec.close()


if __name__ == "__main__":
    main()