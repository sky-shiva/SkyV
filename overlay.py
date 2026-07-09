"""Floating recording indicator for Windows - clean design with timer."""
import tkinter as tk
import time
import math



class Overlay:
    """Floating pill-shaped recording indicator for Windows."""
    
    def __init__(self, level_fn, name="Sky"):
        self.level_fn = level_fn
        self.name = name
        self.is_showing = False
        self._root = None
        self._wave_bars = []
        self._running = False
        self._current_levels = [0] * 12
        self._pulse_phase = 0
        self._start_time = 0
        self._timer_label = None
        
    def show(self):
        """Show recording overlay."""
        if self.is_showing:
            return
        self.is_showing = True
        self._running = True
        self._start_time = time.time()
        self._create_window()
    
    def hide(self):
        """Hide overlay immediately."""
        self.is_showing = False
        self._running = False
        if self._root:
            try:
                self._root.destroy()
            except:
                pass
        self._root = None
        self._wave_bars = []
    
    def _create_window(self):
        """Create the overlay window."""
        if self._root is not None:
            try:
                self._root.destroy()
            except:
                pass
        
        self._root = tk.Tk()
        self._root.overrideredirect(True)
        self._root.attributes('-topmost', True)
        self._root.attributes('-alpha', 0.95)
        self._root.configure(bg='#1a1a2e')
        
        # Window size
        window_width = 350
        window_height = 80
        
        screen_width = self._root.winfo_screenwidth()
        screen_height = self._root.winfo_screenheight()
        x = (screen_width - window_width) // 2
        y = screen_height - window_height - 80
        self._root.geometry(f"{window_width}x{window_height}+{x}+{y}")
        
        # Add rounded border effect with a frame
        border = tk.Frame(
            self._root, 
            bg='#ff4757',  # Red border
            bd=0
        )
        border.pack(fill='both', expand=True, padx=0, pady=0)
        
        inner = tk.Frame(border, bg='#1a1a2e', bd=0)
        inner.pack(fill='both', expand=True, padx=2, pady=2)
        
        # ---- LEFT: Recording dot ----
        dot_area = tk.Frame(inner, bg='#1a1a2e', width=50)
        dot_area.pack(side='left', fill='y')
        dot_area.pack_propagate(False)
        
        self._dot_canvas = tk.Canvas(
            dot_area, width=30, height=30, 
            bg='#1a1a2e', highlightthickness=0
        )
        self._dot_canvas.place(relx=0.5, rely=0.5, anchor='center')
        
        # Red dot
        self._dot = self._dot_canvas.create_oval(5, 5, 25, 25, fill='#ff4757', outline='')
        # Glow ring
        self._dot_glow = self._dot_canvas.create_oval(0, 0, 30, 30, fill='', outline='#ff4757', width=2)
        
        # ---- CENTER: Name + Timer ----
        center = tk.Frame(inner, bg='#1a1a2e')
        center.pack(side='left', padx=10, pady=10)
        
        # Name
        tk.Label(
            center,
            text=self.name,
            font=('Segoe UI', 20, 'bold'),
            fg='#ffffff',
            bg='#1a1a2e'
        ).pack(anchor='w')
        
        # Timer
        self._timer_label = tk.Label(
            center,
            text="00:00",
            font=('Segoe UI', 11),
            fg='#ff4757',
            bg='#1a1a2e'
        )
        self._timer_label.pack(anchor='w')
        
        # ---- RIGHT: Waveform ----
        wave_area = tk.Frame(inner, bg='#1a1a2e', width=160)
        wave_area.pack(side='right', fill='y', padx=5)
        wave_area.pack_propagate(False)
        
        self._wave_canvas = tk.Canvas(
            wave_area, width=150, height=50, 
            bg='#1a1a2e', highlightthickness=0
        )
        self._wave_canvas.place(relx=0.5, rely=0.5, anchor='center')
        
        # Waveform bars
        self._wave_bars = []
        self._bar_positions = []
        num_bars = 12
        for i in range(num_bars):
            x = i * 12 + 5
            self._bar_positions.append(x)
            bar = self._wave_canvas.create_rectangle(
                x, 25, x + 7, 25,
                fill='#ff4757', outline='', width=0
            )
            self._wave_bars.append(bar)
        
        # Start animation
        self._animate()
        self._root.update()
    
    def _animate(self):
        """Main animation loop."""
        if not self._running or not self._root:
            return
        
        try:
            if not self._root.winfo_exists():
                return
        except:
            return
        
        try:
            # Update timer
            elapsed = time.time() - self._start_time
            minutes = int(elapsed // 60)
            seconds = int(elapsed % 60)
            self._timer_label.config(text=f"{minutes:02d}:{seconds:02d}")
            
            # Pulse dot
            self._pulse_phase += 0.1
            pulse = (math.sin(self._pulse_phase) + 1) / 2
            
            # Animate dot size
            size = int(8 + pulse * 3)
            center = 15
            self._dot_canvas.coords(
                self._dot,
                center - size, center - size,
                center + size, center + size
            )
            
            # Glow ring opacity effect (change outline color brightness)
            r = int(255)
            g = int(40 + pulse * 40)
            b = int(50 + pulse * 40)
            glow_color = f'#{r:02x}{g:02x}{b:02x}'
            self._dot_canvas.itemconfig(self._dot_glow, outline=glow_color)
            self._dot_canvas.itemconfig(self._dot, fill=glow_color)
            
            # Get audio level
            try:
                raw_level = self.level_fn() if self.level_fn else 0.15
                raw_level = max(0.05, float(raw_level))
            except:
                raw_level = 0.15
            
            # Animate waveform
            for i in range(len(self._wave_bars)):
                offset = i * 0.6
                variation = 0.3 + 0.7 * abs(math.sin(offset + time.time() * 5))
                target = min(1.0, raw_level * variation * 3.0)
                
                self._current_levels[i] += (target - self._current_levels[i]) * 0.35
                level = self._current_levels[i]
                
                bar_height = max(2, int(30 * level))
                x = self._bar_positions[i]
                y_center = 25
                
                # Red gradient
                g = int(40 + level * 100)
                b = int(50 + level * 100)
                color = f'#ff{g:02x}{b:02x}'
                
                self._wave_canvas.itemconfig(self._wave_bars[i], fill=color)
                self._wave_canvas.coords(
                    self._wave_bars[i],
                    x, y_center - bar_height,
                    x + 7, y_center + bar_height
                )
            
            self._root.update_idletasks()
            self._root.after(30, self._animate)
            
        except:
            pass