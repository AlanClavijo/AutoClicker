import time
import threading
from pynput.mouse import Button, Controller as MouseController, Listener as MouseListener
from pynput.keyboard import Key, KeyCode, Listener as KeyboardListener

class AutoClicker(threading.Thread):
    def __init__(self):
        super().__init__()
        self.mouse = MouseController()
        
        # Concurrency synchronization lock
        self.lock = threading.Lock()
        
        # Click settings
        self.button = Button.left
        self.click_type = "single"  # "single" or "double"
        self.delay = 0.1  # in seconds
        self.repeat_limit = 0  # 0 means infinite
        self.position = None  # None for current location, or (x, y) tuple
        
        # Internal state
        self.running = False
        self.programmatic_click_flag = 0  # Count of programmatic clicks to ignore in listener
        self.auto_click_count = 0
        self.manual_click_count = 0
        
        # Callbacks to notify UI
        self.on_state_change = None  # Callback when start/stop happens (e.g. limit reached)
        self.on_click_registered = None  # Callback when clicks are registered
        
        self.daemon = True
        
    def set_settings(self, button_name, click_type, delay, repeat_limit, position=None):
        """Update settings for the autoclicker."""
        # Map button name
        if button_name.lower() == "left":
            self.button = Button.left
        elif button_name.lower() == "right":
            self.button = Button.right
        elif button_name.lower() == "middle":
            self.button = Button.middle
        else:
            self.button = Button.left
            
        self.click_type = click_type
        self.delay = max(0.001, delay)  # Ensure delay is positive
        self.repeat_limit = repeat_limit
        self.position = position
        
    def start_clicking(self):
        if not self.running:
            self.running = True
            if self.on_state_change:
                self.on_state_change(True)

    def stop_clicking(self):
        if self.running:
            self.running = False
            if self.on_state_change:
                self.on_state_change(False)

    def run(self):
        while True:
            while self.running:
                # Check repeat limit under lock
                with self.lock:
                    current_count = self.auto_click_count
                
                if self.repeat_limit > 0 and current_count >= self.repeat_limit:
                    self.stop_clicking()
                    break
                
                # Move to target position if specified
                if self.position is not None:
                    try:
                        self.mouse.position = self.position
                    except Exception:
                        pass
                
                # Determine click count for pynput
                clicks_to_send = 1 if self.click_type == "single" else 2
                
                # Flag the listener to ignore these upcoming clicks
                with self.lock:
                    self.programmatic_click_flag += clicks_to_send
                
                # Perform the click
                try:
                    if self.click_type == "single":
                        self.mouse.click(self.button, 1)
                    else:
                        self.mouse.click(self.button, 2)
                except Exception:
                    pass
                
                # Wait for the click delay, but support interruptible sleep for responsiveness
                slept = 0
                while slept < self.delay and self.running:
                    sleep_time = min(0.02, self.delay - slept)
                    time.sleep(sleep_time)
                    slept += sleep_time
            time.sleep(0.05)


class ClickerManager:
    def __init__(self, toggle_callback, click_count_callback):
        self.clicker = AutoClicker()
        self.clicker.on_state_change = toggle_callback
        self.clicker.on_click_registered = click_count_callback
        
        self.toggle_callback = toggle_callback
        self.click_count_callback = click_count_callback
        
        # Hotkey configuration (stored as string representation, e.g. "F8")
        self.hotkey_str = "F8"
        self.picking_coordinates = False
        self.coordinate_pick_callback = None
        
        # Listeners
        self.keyboard_listener = None
        self.mouse_listener = None
        
    def start(self):
        """Start the background clicker thread and global listeners."""
        self.clicker.start()
        
        self.keyboard_listener = KeyboardListener(on_press=self._on_key_press)
        self.keyboard_listener.daemon = True
        self.keyboard_listener.start()
        
        self.mouse_listener = MouseListener(on_click=self._on_mouse_click)
        self.mouse_listener.daemon = True
        self.mouse_listener.start()
        
    def stop(self):
        """Cleanly stop listeners and autoclicker to release OS hooks."""
        try:
            self.clicker.stop_clicking()
        except Exception:
            pass
        try:
            if self.keyboard_listener:
                self.keyboard_listener.stop()
        except Exception:
            pass
        try:
            if self.mouse_listener:
                self.mouse_listener.stop()
        except Exception:
            pass
        
    def set_hotkey(self, key_str):
        self.hotkey_str = key_str.upper()
        
    def start_coordinate_picker(self, callback):
        """Activate coordinate picking mode."""
        self.picking_coordinates = True
        self.coordinate_pick_callback = callback
        
    def _on_key_press(self, key):
        try:
            # Handle key press for coordinate picking cancellation
            if self.picking_coordinates:
                if key == Key.esc:
                    self.picking_coordinates = False
                    if self.coordinate_pick_callback:
                        self.coordinate_pick_callback(None)
                    return
                
            # Match hotkey to toggle autoclicking
            if self._matches_hotkey(key, self.hotkey_str):
                if self.clicker.running:
                    self.clicker.stop_clicking()
                else:
                    self.clicker.start_clicking()
        except Exception:
            pass
                
    def _on_mouse_click(self, x, y, button, pressed):
        try:
            if not pressed:
                return
                
            # Handle click for coordinate picking
            if self.picking_coordinates:
                self.picking_coordinates = False
                if self.coordinate_pick_callback:
                    # We defer standard click action during picking
                    self.coordinate_pick_callback((int(x), int(y)))
                return
                
            # Distinguish between programmatic (auto) and manual clicks under lock
            with self.clicker.lock:
                is_programmatic = self.clicker.programmatic_click_flag > 0
                if is_programmatic:
                    self.clicker.programmatic_click_flag -= 1
                    self.clicker.auto_click_count += 1
                    manual_cnt = self.clicker.manual_click_count
                    auto_cnt = self.clicker.auto_click_count
                else:
                    self.clicker.manual_click_count += 1
                    manual_cnt = self.clicker.manual_click_count
                    auto_cnt = self.clicker.auto_click_count
            
            if self.click_count_callback:
                self.click_count_callback(manual_cnt, auto_cnt)
        except Exception:
            pass
                
    def reset_counters(self):
        with self.clicker.lock:
            self.clicker.manual_click_count = 0
            self.clicker.auto_click_count = 0
        if self.click_count_callback:
            self.click_count_callback(0, 0)
            
    def _matches_hotkey(self, key, hotkey_str):
        try:
            # Special keys (F1-F12, Space, etc.)
            if hasattr(key, 'name') and key.name is not None:
                key_name = key.name.upper()
            # Alphanumeric keys
            elif hasattr(key, 'char') and key.char is not None:
                key_name = key.char.upper()
            else:
                key_name = str(key).upper()
                
            # If standard string representation matches
            if key_name == hotkey_str:
                return True
                
            # Fallbacks for specific formatting
            # e.g., Key.f8 -> name is 'f8', hotkey_str is 'F8'
            # Let's check some common aliases
            aliases = {
                "F1": "F1", "F2": "F2", "F3": "F3", "F4": "F4", "F5": "F5", "F6": "F6",
                "F7": "F7", "F8": "F8", "F9": "F9", "F10": "F10", "F11": "F11", "F12": "F12",
                "SPACE": "SPACE", "ENTER": "ENTER", "ESC": "ESC"
            }
            if hotkey_str in aliases:
                # If key name matches the alias name
                return key_name == aliases[hotkey_str]
                
            return False
        except Exception:
            return False
