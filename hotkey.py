"""System-wide push-to-talk hotkey via pynput."""
from pynput import keyboard
import time

KEY_MAP = {
    "alt": keyboard.Key.alt,
    "alt_l": keyboard.Key.alt_l,
    "alt_r": keyboard.Key.alt_r,
    "ctrl": keyboard.Key.ctrl,
    "ctrl_l": keyboard.Key.ctrl_l,
    "ctrl_r": keyboard.Key.ctrl_r,
    "cmd": keyboard.Key.cmd,
    "cmd_l": keyboard.Key.cmd_l,
    "cmd_r": keyboard.Key.cmd_r,
    "shift": keyboard.Key.shift,
    "shift_l": keyboard.Key.shift_l,
    "shift_r": keyboard.Key.shift_r,
    "f13": keyboard.Key.f13,
}

# Groups of equivalent keys
EQUIVALENT_KEYS = {
    keyboard.Key.ctrl: {keyboard.Key.ctrl, keyboard.Key.ctrl_l, keyboard.Key.ctrl_r},
    keyboard.Key.ctrl_l: {keyboard.Key.ctrl, keyboard.Key.ctrl_l, keyboard.Key.ctrl_r},
    keyboard.Key.ctrl_r: {keyboard.Key.ctrl, keyboard.Key.ctrl_l, keyboard.Key.ctrl_r},
    keyboard.Key.shift: {keyboard.Key.shift, keyboard.Key.shift_l, keyboard.Key.shift_r},
    keyboard.Key.shift_l: {keyboard.Key.shift, keyboard.Key.shift_l, keyboard.Key.shift_r},
    keyboard.Key.shift_r: {keyboard.Key.shift, keyboard.Key.shift_l, keyboard.Key.shift_r},
    keyboard.Key.alt: {keyboard.Key.alt, keyboard.Key.alt_l, keyboard.Key.alt_r},
    keyboard.Key.alt_l: {keyboard.Key.alt, keyboard.Key.alt_l, keyboard.Key.alt_r},
    keyboard.Key.alt_r: {keyboard.Key.alt, keyboard.Key.alt_l, keyboard.Key.alt_r},
    keyboard.Key.cmd: {keyboard.Key.cmd, keyboard.Key.cmd_l, keyboard.Key.cmd_r},
    keyboard.Key.cmd_l: {keyboard.Key.cmd, keyboard.Key.cmd_l, keyboard.Key.cmd_r},
    keyboard.Key.cmd_r: {keyboard.Key.cmd, keyboard.Key.cmd_l, keyboard.Key.cmd_r},
}


class PushToTalk:
    def __init__(self, key_name, on_press, on_release, mode="hold"):
        names = [n.strip() for n in key_name.split("+")]
        unknown = [n for n in names if n not in KEY_MAP]
        if unknown:
            raise ValueError(f"Unknown hotkey(s) {unknown}. Choose from: {list(KEY_MAP)}")
        
        # Store the required key types (e.g., "ctrl", "shift")
        self.required_keys = set(names)
        self.mode = mode
        self.on_press_cb = on_press
        self.on_release_cb = on_release
        self._down = set()
        self._chord_held = False
        self._recording = False
        self._last_toggle_time = 0
        self._listener = keyboard.Listener(on_press=self._press, on_release=self._release)

    def _get_key_type(self, key):
        """Map any modifier key to its base type."""
        if key in EQUIVALENT_KEYS:
            # Return all possible names for this key
            return EQUIVALENT_KEYS[key]
        return {key}

    def _check_chord(self):
        """Check if currently held keys match the required chord."""
        if len(self._down) != len(self.required_keys):
            return False
        
        # Get the types of all held keys
        held_types = set()
        for key in self._down:
            if key in EQUIVALENT_KEYS:
                # Add the base name (e.g., "ctrl" for ctrl_l)
                for k in EQUIVALENT_KEYS[key]:
                    for name, mapped_key in KEY_MAP.items():
                        if mapped_key == k:
                            held_types.add(name)
                            break
            else:
                held_types.add(str(key))
        
        # Check if all required keys are present
        for required in self.required_keys:
            # Check if any equivalent key is held
            found = False
            required_key = KEY_MAP[required]
            if required_key in EQUIVALENT_KEYS:
                equivalents = EQUIVALENT_KEYS[required_key]
                for key in self._down:
                    if key in equivalents:
                        found = True
                        break
            else:
                found = required_key in self._down
            
            if not found:
                return False
        
        return True

    def _press(self, key):
        # Map key to its equivalents for consistent tracking
        keys_to_add = self._get_key_type(key)
        
        # Only track modifier keys we care about
        relevant = False
        for required in self.required_keys:
            required_key = KEY_MAP[required]
            if required_key in EQUIVALENT_KEYS:
                if key in EQUIVALENT_KEYS[required_key]:
                    relevant = True
                    break
            elif key == required_key:
                relevant = True
                break
        
        if not relevant:
            return
        
        self._down.add(key)
        
        if not self._chord_held and self._check_chord():
            self._chord_held = True
            
            if self.mode == "toggle":
                current_time = time.time()
                if current_time - self._last_toggle_time < 0.5:
                    return
                self._last_toggle_time = current_time
                
                if self._recording:
                    self._recording = False
                    self.on_release_cb()
                else:
                    self._recording = True
                    self.on_press_cb()
            else:  # hold
                self._recording = True
                self.on_press_cb()

    def _release(self, key):
        self._down.discard(key)
        
        if self._chord_held and not self._check_chord():
            self._chord_held = False
            if self.mode == "hold" and self._recording:
                self._recording = False
                self.on_release_cb()

    def start(self):
        self._listener.start()

    def run(self):
        self._listener.start()
        self._listener.join()