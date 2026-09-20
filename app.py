import sys
import os
import threading
import customtkinter as ctk
from clicker import ClickerManager

# Initialize customtkinter settings
ctk.set_appearance_mode("dark")  # Default mode
ctk.set_default_color_theme("blue")  # Default color theme

def play_toggle_sound(active):
    """Play a short diagnostic beep on Windows when clicking toggles in a background thread."""
    def _beep():
        if sys.platform == "win32":
            import winsound
            try:
                if active:
                    winsound.Beep(1000, 120)  # Pitch: 1000Hz, Duration: 120ms
                else:
                    winsound.Beep(600, 150)   # Pitch: 600Hz, Duration: 150ms
            except Exception:
                pass
    # Execute in a daemon thread so it doesn't block the main GUI loop
    threading.Thread(target=_beep, daemon=True).start()

class AutoclickerApp(ctk.CTk):
    def __init__(self):
        super().__init__()
        
        # Force Windows to associate the window with a custom App ID for taskbar icon grouping
        if sys.platform == "win32":
            import ctypes
            try:
                myappid = 'aslandev.autoclicker.gui.1.0'
                ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(myappid)
            except Exception:
                pass
        
        # Configure Main Window
        self.title("Auto Clicker by AslanDev")
        self.geometry("740x440")
        self.resizable(False, False)
        
        # Load and set titlebar icon
        icon_path = "app_icon.ico"
        if os.path.exists(icon_path):
            try:
                self.iconbitmap(icon_path)
            except Exception:
                pass
        
        # Current settings state
        self.current_hotkey = "F8"
        
        # Initialize the background clicker manager
        # Pass thread-safe callbacks using self.after
        self.manager = ClickerManager(
            toggle_callback=self.on_clicker_state_change,
            click_count_callback=self.on_click_registered
        )
        
        # Start background threads and input listeners
        self.manager.start()
        
        # Configure layout grids
        self.grid_columnconfigure(0, weight=3) # Left Settings Section
        self.grid_columnconfigure(1, weight=2) # Right Action/Stats Section
        self.grid_rowconfigure(0, weight=1)
        
        # Setup UI Components
        self.setup_left_panel()
        self.setup_right_panel()
        
        # Default settings update to Clicker Thread
        self.apply_settings()
        
    def setup_left_panel(self):
        """Build the configurations, settings and tabs panel."""
        self.left_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.left_frame.grid(row=0, column=0, padx=(15, 7), pady=15, sticky="nsew")
        
        # App Title/Header
        self.header_label = ctk.CTkLabel(
            self.left_frame, 
            text="AUTOCLICKER by AslanDev",
            font=ctk.CTkFont(family="Segoe UI", size=20, weight="bold")
        )
        self.header_label.pack(anchor="w", padx=10, pady=(5, 10))
        
        # Tab View
        self.tabview = ctk.CTkTabview(self.left_frame)
        self.tabview.pack(fill="both", expand=True)
        
        self.tab_click = self.tabview.add("Click Settings")
        self.tab_position = self.tabview.add("Click Location")
        self.tab_options = self.tabview.add("Preferences")
        
        self.setup_click_settings_tab()
        self.setup_click_position_tab()
        self.setup_preferences_tab()
        
    def setup_click_settings_tab(self):
        """Click Settings Tab Layout."""
        # Validation for integer entry inputs
        digit_val_cmd = (self.register(self._validate_only_digits), "%S")
        
        # 1. Click Interval Frame
        interval_frame = ctk.CTkFrame(self.tab_click, fg_color="transparent")
        interval_frame.pack(fill="x", padx=10, pady=5)
        
        interval_title = ctk.CTkLabel(
            interval_frame, 
            text="Click Interval:", 
            font=ctk.CTkFont(family="Segoe UI", size=13, weight="bold")
        )
        interval_title.pack(anchor="w", pady=(0, 5))
        
        # Flex layout for Hours, Minutes, Seconds, Milliseconds
        inputs_subframe = ctk.CTkFrame(interval_frame, fg_color="transparent")
        inputs_subframe.pack(fill="x")
        
        # Input boxes styling
        input_width = 65
        
        # Hours
        h_frame = ctk.CTkFrame(inputs_subframe, fg_color="transparent")
        h_frame.pack(side="left", padx=(0, 10))
        self.entry_hours = ctk.CTkEntry(h_frame, width=input_width, placeholder_text="0", validate="key", validatecommand=digit_val_cmd)
        self.entry_hours.pack()
        self.entry_hours.insert(0, "0")
        ctk.CTkLabel(h_frame, text="Hours", font=ctk.CTkFont(size=10)).pack(pady=2)
        
        # Minutes
        m_frame = ctk.CTkFrame(inputs_subframe, fg_color="transparent")
        m_frame.pack(side="left", padx=(0, 10))
        self.entry_mins = ctk.CTkEntry(m_frame, width=input_width, placeholder_text="0", validate="key", validatecommand=digit_val_cmd)
        self.entry_mins.pack()
        self.entry_mins.insert(0, "0")
        ctk.CTkLabel(m_frame, text="Mins", font=ctk.CTkFont(size=10)).pack(pady=2)
        
        # Seconds
        s_frame = ctk.CTkFrame(inputs_subframe, fg_color="transparent")
        s_frame.pack(side="left", padx=(0, 10))
        self.entry_secs = ctk.CTkEntry(s_frame, width=input_width, placeholder_text="0", validate="key", validatecommand=digit_val_cmd)
        self.entry_secs.pack()
        self.entry_secs.insert(0, "0")
        ctk.CTkLabel(s_frame, text="Secs", font=ctk.CTkFont(size=10)).pack(pady=2)
        
        # Milliseconds
        ms_frame = ctk.CTkFrame(inputs_subframe, fg_color="transparent")
        ms_frame.pack(side="left")
        self.entry_ms = ctk.CTkEntry(ms_frame, width=input_width, placeholder_text="100", validate="key", validatecommand=digit_val_cmd)
        self.entry_ms.pack()
        self.entry_ms.insert(0, "100")
        ctk.CTkLabel(ms_frame, text="Ms", font=ctk.CTkFont(size=10)).pack(pady=2)
        
        # Bind change events to apply settings instantly
        for entry in [self.entry_hours, self.entry_mins, self.entry_secs, self.entry_ms]:
            entry.bind("<KeyRelease>", lambda e: self.apply_settings())
            
        # 2. Click Options Frame (Mouse Button & Click Type)
        options_frame = ctk.CTkFrame(self.tab_click, fg_color="transparent")
        options_frame.pack(fill="x", padx=10, pady=10)
        
        btn_label = ctk.CTkLabel(options_frame, text="Mouse Button:", font=ctk.CTkFont(family="Segoe UI", size=13, weight="bold"))
        btn_label.grid(row=0, column=0, sticky="w", pady=(0, 2))
        
        type_label = ctk.CTkLabel(options_frame, text="Click Type:", font=ctk.CTkFont(family="Segoe UI", size=13, weight="bold"))
        type_label.grid(row=0, column=1, sticky="w", pady=(0, 2), padx=(20, 0))
        
        self.mouse_btn_select = ctk.CTkSegmentedButton(
            options_frame, 
            values=["Left", "Middle", "Right"],
            command=lambda v: self.apply_settings()
        )
        self.mouse_btn_select.grid(row=1, column=0, sticky="ew", pady=(0, 5))
        self.mouse_btn_select.set("Left")
        
        self.click_type_select = ctk.CTkSegmentedButton(
            options_frame, 
            values=["Single", "Double"],
            command=lambda v: self.apply_settings()
        )
        self.click_type_select.grid(row=1, column=1, sticky="ew", pady=(0, 5), padx=(20, 0))
        self.click_type_select.set("Single")
        
        # 3. Repeat Options Frame
        repeat_frame = ctk.CTkFrame(self.tab_click, fg_color="transparent")
        repeat_frame.pack(fill="x", padx=10, pady=5)
        
        repeat_title = ctk.CTkLabel(
            repeat_frame, 
            text="Repeat Limit:", 
            font=ctk.CTkFont(family="Segoe UI", size=13, weight="bold")
        )
        repeat_title.pack(anchor="w", pady=(0, 2))
        
        self.repeat_mode = ctk.StringVar(value="infinite")
        
        self.radio_infinite = ctk.CTkRadioButton(
            repeat_frame, 
            text="Repeat until stopped", 
            variable=self.repeat_mode, 
            value="infinite",
            command=self.on_repeat_mode_change
        )
        self.radio_infinite.pack(anchor="w", pady=2)
        
        limit_subframe = ctk.CTkFrame(repeat_frame, fg_color="transparent")
        limit_subframe.pack(anchor="w", fill="x", pady=2)
        
        self.radio_times = ctk.CTkRadioButton(
            limit_subframe, 
            text="Repeat ", 
            variable=self.repeat_mode, 
            value="count",
            command=self.on_repeat_mode_change
        )
        self.radio_times.pack(side="left")
        
        self.entry_repeat_count = ctk.CTkEntry(
            limit_subframe, 
            width=65, 
            validate="key", 
            validatecommand=digit_val_cmd,
            state="disabled"
        )
        self.entry_repeat_count.pack(side="left", padx=5)
        self.entry_repeat_count.insert(0, "10")
        self.entry_repeat_count.bind("<KeyRelease>", lambda e: self.apply_settings())
        
        ctk.CTkLabel(limit_subframe, text="times").pack(side="left")
        
    def setup_click_position_tab(self):
        """Click Location Tab Layout."""
        digit_val_cmd = (self.register(self._validate_only_digits), "%S")
        
        self.position_mode = ctk.StringVar(value="current")
        
        radio_curr = ctk.CTkRadioButton(
            self.tab_position, 
            text="Click at current cursor location", 
            variable=self.position_mode, 
            value="current",
            command=self.on_position_mode_change
        )
        radio_curr.pack(anchor="w", padx=10, pady=10)
        
        radio_fixed = ctk.CTkRadioButton(
            self.tab_position, 
            text="Click at fixed coordinates", 
            variable=self.position_mode, 
            value="fixed",
            command=self.on_position_mode_change
        )
        radio_fixed.pack(anchor="w", padx=10, pady=(5, 10))
        
        # Coordinates frame
        coords_frame = ctk.CTkFrame(self.tab_position, fg_color="transparent")
        coords_frame.pack(anchor="w", fill="x", padx=30, pady=5)
        
        ctk.CTkLabel(coords_frame, text="X:").pack(side="left", padx=(0, 5))
        self.entry_x = ctk.CTkEntry(coords_frame, width=65, validate="key", validatecommand=digit_val_cmd, state="disabled")
        self.entry_x.pack(side="left", padx=(0, 15))
        self.entry_x.insert(0, "0")
        self.entry_x.bind("<KeyRelease>", lambda e: self.apply_settings())
        
        ctk.CTkLabel(coords_frame, text="Y:").pack(side="left", padx=(0, 5))
        self.entry_y = ctk.CTkEntry(coords_frame, width=65, validate="key", validatecommand=digit_val_cmd, state="disabled")
        self.entry_y.pack(side="left", padx=(0, 15))
        self.entry_y.insert(0, "0")
        self.entry_y.bind("<KeyRelease>", lambda e: self.apply_settings())
        
        # Pick Coordinates button
        self.btn_pick_coords = ctk.CTkButton(
            self.tab_position, 
            text="Pick Coordinates", 
            fg_color="#3498db",
            hover_color="#2980b9",
            state="disabled",
            command=self.trigger_coordinate_picker
        )
        self.btn_pick_coords.pack(anchor="w", padx=30, pady=15)
        
    def setup_preferences_tab(self):
        """Preferences / Settings Tab Layout."""
        # 1. Hotkey Selection
        hotkey_frame = ctk.CTkFrame(self.tab_options, fg_color="transparent")
        hotkey_frame.pack(fill="x", padx=10, pady=10)
        
        ctk.CTkLabel(
            hotkey_frame, 
            text="Toggle Hotkey:", 
            font=ctk.CTkFont(family="Segoe UI", size=13, weight="bold")
        ).pack(side="left", padx=(0, 15))
        
        hotkeys_list = ["F1", "F2", "F3", "F4", "F5", "F6", "F7", "F8", "F9", "F10", "F11", "F12", "Space", "Enter", "Esc"]
        self.hotkey_selector = ctk.CTkComboBox(
            hotkey_frame, 
            values=hotkeys_list,
            width=100,
            command=self.on_hotkey_change
        )
        self.hotkey_selector.pack(side="left")
        self.hotkey_selector.set("F8")
        
        # 2. Sound Toggle
        self.sound_enabled = ctk.BooleanVar(value=True)
        self.sound_chk = ctk.CTkCheckBox(
            self.tab_options, 
            text="Play audio click-toggle sound feedback", 
            variable=self.sound_enabled
        )
        self.sound_chk.pack(anchor="w", padx=10, pady=10)
        
        # 3. Theme Toggle
        theme_frame = ctk.CTkFrame(self.tab_options, fg_color="transparent")
        theme_frame.pack(fill="x", padx=10, pady=5)
        
        ctk.CTkLabel(theme_frame, text="Appearance Mode:").pack(side="left", padx=(0, 15))
        self.theme_selector = ctk.CTkComboBox(
            theme_frame, 
            values=["Dark", "Light"],
            width=100,
            command=self.on_theme_change
        )
        self.theme_selector.pack(side="left")
        self.theme_selector.set("Dark")
        
    def setup_right_panel(self):
        """Build the visual status, big start button and stats display panel."""
        self.right_frame = ctk.CTkFrame(self, fg_color="#232329", corner_radius=12)
        self.right_frame.grid(row=0, column=1, padx=(7, 15), pady=15, sticky="nsew")
        
        # Main Status Badge
        status_card = ctk.CTkFrame(self.right_frame, fg_color="#2C2C35", corner_radius=8)
        status_card.pack(fill="x", padx=15, pady=(15, 10))
        
        status_label = ctk.CTkLabel(status_card, text="STATUS:", font=ctk.CTkFont(family="Segoe UI", size=11, weight="bold"))
        status_label.pack(side="left", padx=(15, 10), pady=10)
        
        # Pulsing circle dot
        self.status_dot = ctk.CTkFrame(status_card, width=12, height=12, corner_radius=6, fg_color="#e74c3c")
        self.status_dot.pack(side="left", padx=(0, 5))
        
        self.status_text = ctk.CTkLabel(status_card, text="IDLE", font=ctk.CTkFont(family="Segoe UI", size=13, weight="bold"), text_color="#e74c3c")
        self.status_text.pack(side="left")
        
        # Massive START / STOP action button
        self.start_btn = ctk.CTkButton(
            self.right_frame, 
            text="START (F8)",
            font=ctk.CTkFont(family="Segoe UI", size=18, weight="bold"),
            height=60,
            fg_color="#2ecc71",
            hover_color="#27ae60",
            command=self.toggle_clicking
        )
        self.start_btn.pack(fill="x", padx=15, pady=10)
        
        # Click Counters Cards
        counters_frame = ctk.CTkFrame(self.right_frame, fg_color="#2C2C35", corner_radius=8)
        counters_frame.pack(fill="both", expand=True, padx=15, pady=(5, 15))
        
        # Manual clicks box
        manual_box = ctk.CTkFrame(counters_frame, fg_color="transparent")
        manual_box.pack(fill="x", padx=15, pady=(15, 5))
        
        ctk.CTkLabel(
            manual_box, 
            text="Manual Clicks", 
            font=ctk.CTkFont(family="Segoe UI", size=12, weight="bold")
        ).pack(side="left")
        
        self.manual_counter_lbl = ctk.CTkLabel(
            manual_box, 
            text="0", 
            font=ctk.CTkFont(family="Consolas", size=24, weight="bold"),
            text_color="#3498db"
        )
        self.manual_counter_lbl.pack(side="right")
        
        # Auto clicks box
        auto_box = ctk.CTkFrame(counters_frame, fg_color="transparent")
        auto_box.pack(fill="x", padx=15, pady=5)
        
        ctk.CTkLabel(
            auto_box, 
            text="Auto Clicks", 
            font=ctk.CTkFont(family="Segoe UI", size=12, weight="bold")
        ).pack(side="left")
        
        self.auto_counter_lbl = ctk.CTkLabel(
            auto_box, 
            text="0", 
            font=ctk.CTkFont(family="Consolas", size=24, weight="bold"),
            text_color="#2ecc71"
        )
        self.auto_counter_lbl.pack(side="right")
        
        # Divider line
        divider = ctk.CTkFrame(counters_frame, height=2, fg_color="#3E3E4A")
        divider.pack(fill="x", padx=15, pady=10)
        
        # Reset counters button
        self.btn_reset = ctk.CTkButton(
            counters_frame, 
            text="Reset Counters",
            font=ctk.CTkFont(family="Segoe UI", size=12),
            height=28,
            fg_color="#3E3E4A",
            hover_color="#505060",
            command=self.reset_counters
        )
        self.btn_reset.pack(fill="x", padx=15, pady=(0, 15))
        
    def _validate_only_digits(self, text):
        """Helper callback for validating numerical entries only."""
        return text.isdigit() or text == ""
        
    def apply_settings(self):
        """Read all GUI parameters and pass them down to the Autoclicker thread."""
        try:
            # Parse Interval Delay
            hours = int(self.entry_hours.get() or 0)
            mins = int(self.entry_mins.get() or 0)
            secs = int(self.entry_secs.get() or 0)
            ms = int(self.entry_ms.get() or 0)
        except ValueError:
            hours, mins, secs, ms = 0, 0, 0, 100
            
        total_delay = hours * 3600 + mins * 60 + secs + (ms / 1000.0)
        
        # Mouse settings
        button_name = self.mouse_btn_select.get()
        click_type = self.click_type_select.get().lower()
        
        # Repeat settings
        if self.repeat_mode.get() == "infinite":
            repeat_limit = 0
        else:
            try:
                repeat_limit = int(self.entry_repeat_count.get() or 0)
            except ValueError:
                repeat_limit = 0
                
        # Position settings
        position = None
        if self.position_mode.get() == "fixed":
            try:
                x = int(self.entry_x.get() or 0)
                y = int(self.entry_y.get() or 0)
                position = (x, y)
            except ValueError:
                position = (0, 0)
                
        # Apply to thread manager
        self.manager.clicker.set_settings(
            button_name=button_name,
            click_type=click_type,
            delay=total_delay,
            repeat_limit=repeat_limit,
            position=position
        )
        
    def on_repeat_mode_change(self):
        """Enable/Disable Repeat Limit entry depending on the selected radio button."""
        if self.repeat_mode.get() == "count":
            self.entry_repeat_count.configure(state="normal")
        else:
            self.entry_repeat_count.configure(state="disabled")
        self.apply_settings()
        
    def on_position_mode_change(self):
        """Enable/Disable coordinates fields depending on position radio buttons."""
        if self.position_mode.get() == "fixed":
            self.entry_x.configure(state="normal")
            self.entry_y.configure(state="normal")
            self.btn_pick_coords.configure(state="normal")
        else:
            self.entry_x.configure(state="disabled")
            self.entry_y.configure(state="disabled")
            self.btn_pick_coords.configure(state="disabled")
        self.apply_settings()
        
    def on_hotkey_change(self, value):
        """Update global hotkey listener with the selected key."""
        self.current_hotkey = value.upper()
        self.manager.set_hotkey(value)
        # Update Start/Stop button label with the new hotkey
        is_running = self.manager.clicker.running
        prefix = "STOP" if is_running else "START"
        self.start_btn.configure(text=f"{prefix} ({self.current_hotkey})")
        
    def on_theme_change(self, value):
        """Change appearance mode dynamically (Dark/Light)."""
        ctk.set_appearance_mode(value.lower())
        
    def toggle_clicking(self):
        """Start/Stop clicking manually from button click."""
        if self.manager.clicker.running:
            self.manager.clicker.stop_clicking()
        else:
            # Re-apply settings before starting to ensure latest inputs are captured
            self.apply_settings()
            self.manager.clicker.start_clicking()
            
    def on_clicker_state_change(self, active):
        """Thread-safe UI state update callback triggered by the autoclicker thread."""
        self.after(0, self._update_ui_state, active)
        
    def _update_ui_state(self, active):
        """Update GUI elements representing running/idle state."""
        if active:
            # Active State
            self.status_dot.configure(fg_color="#2ecc71") # Green indicator
            self.status_text.configure(text="ACTIVE", text_color="#2ecc71")
            self.start_btn.configure(
                text=f"STOP ({self.current_hotkey})", 
                fg_color="#e74c3c", 
                hover_color="#c0392b"
            )
            if self.sound_enabled.get():
                play_toggle_sound(True)
        else:
            # Inactive State
            self.status_dot.configure(fg_color="#e74c3c") # Red indicator
            self.status_text.configure(text="IDLE", text_color="#e74c3c")
            self.start_btn.configure(
                text=f"START ({self.current_hotkey})", 
                fg_color="#2ecc71", 
                hover_color="#27ae60"
            )
            if self.sound_enabled.get():
                play_toggle_sound(False)
                
    def on_click_registered(self, manual_count, auto_count):
        """Thread-safe callback to refresh counters."""
        self.after(0, self._update_counters_ui, manual_count, auto_count)
        
    def _update_counters_ui(self, manual, auto):
        self.manual_counter_lbl.configure(text=str(manual))
        self.auto_counter_lbl.configure(text=str(auto))
        
    def reset_counters(self):
        """Reset both clicks statistics."""
        self.manager.reset_counters()
        
    def trigger_coordinate_picker(self):
        """Show full screen transparent overlay to select coordinates in a thread-safe way."""
        # Hide the main window
        self.withdraw()
        
        # Create full screen frameless top-level window
        self.picker_overlay = ctk.CTkToplevel(self)
        self.picker_overlay.overrideredirect(True)
        self.picker_overlay.state("zoomed") # Maximized
        self.picker_overlay.attributes("-alpha", 0.4) # Transparent overlay
        self.picker_overlay.configure(fg_color="black")
        self.picker_overlay.attributes("-topmost", True)
        
        # Label with visual guide
        label_text = (
            "COORDINATE PICKER MODE\n\n"
            "1. Move your mouse to the desired position on screen.\n"
            "2. Left-click anywhere to capture the coordinates.\n"
            "3. Press ESC to cancel and return."
        )
        label = ctk.CTkLabel(
            self.picker_overlay,
            text=label_text,
            font=ctk.CTkFont(family="Segoe UI", size=20, weight="bold"),
            text_color="#ffffff",
            justify="center"
        )
        label.pack(expand=True)
        
        # Activate picking mode with thread-safe wrapper using self.after
        self.manager.start_coordinate_picker(
            lambda coords: self.after(0, self.on_coordinate_picked, coords)
        )
        
        # Bind ESC and mouse click directly on the overlay window
        self.picker_overlay.bind("<Button-1>", self._on_overlay_click)
        self.picker_overlay.bind("<Escape>", self._on_overlay_escape)
        self.picker_overlay.focus_force()
        
    def _on_overlay_click(self, event):
        # Let ClickerManager capture click coordinate globally first.
        pass
        
    def _on_overlay_escape(self, event):
        self.on_coordinate_picked(None)
        
    def on_coordinate_picked(self, coords):
        """Callback from coordinate picking. Guaranteed to run on Tkinter's main thread."""
        if hasattr(self, "picker_overlay") and self.picker_overlay:
            try:
                self.picker_overlay.destroy()
            except Exception:
                pass
            self.picker_overlay = None
            
        # Restore main window
        self.deiconify()
        self.focus_force()
        
        if coords is not None:
            x, y = coords
            # Update coordinate inputs
            self.entry_x.configure(state="normal")
            self.entry_y.configure(state="normal")
            
            self.entry_x.delete(0, "end")
            self.entry_x.insert(0, str(x))
            
            self.entry_y.delete(0, "end")
            self.entry_y.insert(0, str(y))
            
            self.apply_settings()

if __name__ == "__main__":
    app = AutoclickerApp()
    # Handle clean termination of listeners when window is closed
    def on_closing():
        try:
            # Stop global listeners and clicker thread cleanly
            app.manager.stop()
        except Exception:
            pass
        try:
            app.destroy()
        except Exception:
            pass
        sys.exit(0)
        
    app.protocol("WM_DELETE_WINDOW", on_closing)
    app.mainloop()
