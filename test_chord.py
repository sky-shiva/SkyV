from pynput import keyboard
import time

# Test if Ctrl+Shift is detected
current_keys = set()




def on_press(key):
    current_keys.add(key)
    print(f"Keys held: {current_keys}")
    
    # Check for Ctrl+Shift (all combinations)
    ctrl_keys = {keyboard.Key.ctrl, keyboard.Key.ctrl_l, keyboard.Key.ctrl_r}
    shift_keys = {keyboard.Key.shift, keyboard.Key.shift_l, keyboard.Key.shift_r}
    
    has_ctrl = bool(current_keys & ctrl_keys)
    has_shift = bool(current_keys & shift_keys)
    
    if has_ctrl and has_shift:
        print("✅ CTRL+SHIFT DETECTED!")

def on_release(key):
    current_keys.discard(key)
    if key == keyboard.Key.esc:
        return False

print("Press Ctrl+Shift to test. Press ESC to exit.")
with keyboard.Listener(on_press=on_press, on_release=on_release) as listener:
    listener.join()