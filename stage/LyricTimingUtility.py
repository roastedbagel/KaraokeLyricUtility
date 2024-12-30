import tkinter as tk
from tkinter import ttk, scrolledtext, colorchooser
import time
import json
from datetime import datetime
from tkinter import font as tkfont

class ColorConfigFrame(ttk.LabelFrame):
    def __init__(self, parent, title, initial_color, callback):
        super().__init__(parent, text=title)
        self.callback = callback
        self.color = initial_color
        
        self.color_btn = ttk.Button(self, text="Choose Color", command=self.choose_color)
        self.color_btn.grid(row=0, column=0, padx=5, pady=5)
        
        self.preview = tk.Label(self, text="Preview", width=10, bg=initial_color)
        self.preview.grid(row=0, column=1, padx=5, pady=5)
        
    def choose_color(self):
        color = colorchooser.askcolor(color=self.color)[1]
        if color:
            self.color = color
            self.preview.configure(bg=color)
            self.callback(color)

class LyricPreviewFrame(ttk.Frame):
    def __init__(self, parent):
        super().__init__(parent)
        self.preview_text = tk.Text(self, height=3, width=50, wrap=tk.WORD)
        self.preview_text.pack(padx=5, pady=5)
        self.preview_text.tag_configure('sung', foreground='red')
        
    def update_preview(self, text, sung_percentage=0):
        self.preview_text.delete('1.0', tk.END)
        self.preview_text.insert('1.0', text)
        if sung_percentage > 0:
            # Calculate how many characters to highlight
            total_chars = len(text)
            chars_to_highlight = int(total_chars * sung_percentage / 100)
            self.preview_text.tag_add('sung', '1.0', f'1.{chars_to_highlight}')

class FontConfigFrame(ttk.LabelFrame):
    def __init__(self, parent, callback):
        super().__init__(parent, text="Font Configuration")
        self.callback = callback
        
        # Font family
        ttk.Label(self, text="Font:").grid(row=0, column=0, padx=5, pady=5)
        self.font_family = ttk.Combobox(self, values=sorted(tkfont.families()))
        self.font_family.set('Arial')
        self.font_family.grid(row=0, column=1, padx=5, pady=5)
        
        # Font size
        ttk.Label(self, text="Size:").grid(row=0, column=2, padx=5, pady=5)
        self.font_size = ttk.Spinbox(self, from_=8, to=72, width=5)
        self.font_size.set(12)
        self.font_size.grid(row=0, column=3, padx=5, pady=5)
        
        # Update button
        ttk.Button(self, text="Update Font", command=self.update_font).grid(row=0, column=4, padx=5, pady=5)
        
    def update_font(self):
        self.callback(self.font_family.get(), int(self.font_size.get()))

class LyricTimingTool:
    def __init__(self, root):
        self.root = root
        self.root.title("Lyrics Timing Tool")
        
        # Configuration
        self.config = {
            'background_color': '#FFFFFF',
            'text_color': '#000000',
            'highlight_color': '#FF0000',
            'font_family': 'Arial',
            'font_size': 12
        }
        
        # Data storage
        self.start_time = None
        self.is_running = False
        self.timestamps = []
        self.current_line = 0
        
        # Setup UI
        self.setup_ui()
        
    def setup_ui(self):
        # Main container with padding
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Configuration section
        config_frame = ttk.LabelFrame(main_frame, text="Configuration")
        config_frame.grid(row=0, column=0, pady=5, sticky=(tk.W, tk.E))
        
        # Color configuration
        colors_frame = ttk.Frame(config_frame)
        colors_frame.pack(fill=tk.X, padx=5, pady=5)
        
        self.bg_color_config = ColorConfigFrame(
            colors_frame, "Background Color", 
            self.config['background_color'],
            lambda c: self.update_config('background_color', c)
        )
        self.bg_color_config.grid(row=0, column=0, padx=5)
        
        self.text_color_config = ColorConfigFrame(
            colors_frame, "Text Color",
            self.config['text_color'],
            lambda c: self.update_config('text_color', c)
        )
        self.text_color_config.grid(row=0, column=1, padx=5)
        
        self.highlight_color_config = ColorConfigFrame(
            colors_frame, "Highlight Color",
            self.config['highlight_color'],
            lambda c: self.update_config('highlight_color', c)
        )
        self.highlight_color_config.grid(row=0, column=2, padx=5)
        
        # Font configuration
        self.font_config = FontConfigFrame(config_frame, self.update_font)
        self.font_config.pack(fill=tk.X, padx=5, pady=5)
        
        # Preview section
        preview_frame = ttk.LabelFrame(main_frame, text="Live Preview")
        preview_frame.grid(row=1, column=0, pady=5, sticky=(tk.W, tk.E))
        self.preview = LyricPreviewFrame(preview_frame)
        self.preview.pack(fill=tk.X, padx=5, pady=5)
        
        # Lyrics input
        ttk.Label(main_frame, text="Enter lyrics (one line per row):").grid(row=2, column=0, pady=5)
        self.lyrics_text = scrolledtext.ScrolledText(main_frame, width=50, height=10)
        self.lyrics_text.grid(row=3, column=0, pady=5)
        
        # Controls frame
        controls_frame = ttk.Frame(main_frame)
        controls_frame.grid(row=4, column=0, pady=10)
        
        # Timer display
        self.timer_var = tk.StringVar(value="00:00.000")
        timer_label = ttk.Label(controls_frame, textvariable=self.timer_var, font=('Courier', 20))
        timer_label.grid(row=0, column=0, columnspan=3, pady=10)
        
        # Control buttons
        self.start_button = ttk.Button(controls_frame, text="Start", command=self.start_timing)
        self.start_button.grid(row=1, column=0, padx=5)
        
        self.mark_button = ttk.Button(controls_frame, text="Mark", command=self.mark_timestamp, state='disabled')
        self.mark_button.grid(row=1, column=1, padx=5)
        
        self.stop_button = ttk.Button(controls_frame, text="Stop", command=self.stop_timing, state='disabled')
        self.stop_button.grid(row=1, column=2, padx=5)
        
        # Results display
        ttk.Label(main_frame, text="Timing Results:").grid(row=5, column=0, pady=5)
        self.results_text = scrolledtext.ScrolledText(main_frame, width=50, height=10)
        self.results_text.grid(row=6, column=0, pady=5)
        
        # Export button
        ttk.Button(main_frame, text="Export", command=self.export_timestamps).grid(row=7, column=0, pady=10)
        
    def update_config(self, key, value):
        self.config[key] = value
        self.apply_styling()
        
    def update_font(self, family, size):
        self.config['font_family'] = family
        self.config['font_size'] = size
        self.apply_styling()
        
    def apply_styling(self):
        font_config = (self.config['font_family'], self.config['font_size'])
        
        # Update preview styling
        self.preview.preview_text.configure(
            bg=self.config['background_color'],
            fg=self.config['text_color'],
            font=font_config
        )
        self.preview.preview_text.tag_configure(
            'sung',
            foreground=self.config['highlight_color']
        )
        
        # Update other text widgets
        self.lyrics_text.configure(
            bg=self.config['background_color'],
            fg=self.config['text_color'],
            font=font_config
        )
        self.results_text.configure(
            bg=self.config['background_color'],
            fg=self.config['text_color'],
            font=font_config
        )
        
    def start_timing(self):
        self.lyrics = self.lyrics_text.get('1.0', tk.END).strip().split('\n')
        if not self.lyrics or self.lyrics[0] == '':
            return
            
        self.start_time = time.time()
        self.is_running = True
        self.current_line = 0
        self.timestamps = []
        
        self.start_button.config(state='disabled')
        self.mark_button.config(state='normal')
        self.stop_button.config(state='normal')
        self.update_timer()
        self.update_preview_text()
        
    def mark_timestamp(self):
        if not self.is_running:
            return
            
        current_time = time.time() - self.start_time
        if self.current_line < len(self.lyrics):
            self.timestamps.append({
                'time': current_time,
                'text': self.lyrics[self.current_line],
                'styling': {
                    'background_color': self.config['background_color'],
                    'text_color': self.config['text_color'],
                    'highlight_color': self.config['highlight_color'],
                    'font_family': self.config['font_family'],
                    'font_size': self.config['font_size']
                }
            })
            self.current_line += 1
            self.update_preview_text()
            self.update_results()
            
        if self.current_line >= len(self.lyrics):
            self.stop_timing()
            
    def update_preview_text(self):
        if self.current_line < len(self.lyrics):
            self.preview.preview_text.delete('1.0', tk.END)
            self.preview.preview_text.insert('1.0', self.lyrics[self.current_line])
            # Simulate progressive highlighting
            if self.is_running:
                elapsed = (time.time() - self.start_time) % 1.0  # Use modulo for continuous animation
                self.preview.update_preview(self.lyrics[self.current_line], elapsed * 100)
                self.root.after(50, self.update_preview_text)  # Update animation
                
    def stop_timing(self):
        self.is_running = False
        self.start_button.config(state='normal')
        self.mark_button.config(state='disabled')
        self.stop_button.config(state='disabled')
        
    def update_timer(self):
        if self.is_running:
            elapsed = time.time() - self.start_time
            minutes = int(elapsed // 60)
            seconds = elapsed % 60
            self.timer_var.set(f"{minutes:02d}:{seconds:06.3f}")
            self.root.after(10, self.update_timer)
            
    def update_results(self):
        self.results_text.delete('1.0', tk.END)
        for ts in self.timestamps:
            minutes = int(ts['time'] // 60)
            seconds = ts['time'] % 60
            self.results_text.insert(tk.END, f"{minutes:02d}:{seconds:06.3f} - {ts['text']}\n")
            
    def export_timestamps(self):
        if not self.timestamps:
            return
            
        filename = f"lyrics_timing_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(filename, 'w') as f:
            json.dump({
                'timestamps': self.timestamps,
                'config': self.config
            }, f, indent=2)

def main():
    root = tk.Tk()
    app = LyricTimingTool(root)
    root.mainloop()

if __name__ == "__main__":
    main()