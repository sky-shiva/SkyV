"""Text injection at the cursor: clipboard + Ctrl+V (Windows)."""
import time
import pyperclip
from pynput.keyboard import Controller, Key




def inject(text, cfg):
    if not text:
        return
    
    # Save old clipboard
    try:
        old_clipboard = pyperclip.paste()
    except:
        old_clipboard = None
    
    # Copy text to clipboard
    pyperclip.copy(text)
    time.sleep(0.05)
    
    # Press Ctrl+V to paste
    keyboard = Controller()
    keyboard.press(Key.ctrl)
    keyboard.press('v')
    keyboard.release('v')
    keyboard.release(Key.ctrl)
    
    # Restore old clipboard if needed
    if old_clipboard is not None and cfg.get("restore_clipboard", True):
        time.sleep(0.25)
        pyperclip.copy(old_clipboard)