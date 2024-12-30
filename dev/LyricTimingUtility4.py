import tkinter as tk
from tkinter import ttk, scrolledtext, colorchooser
import time
import json
from datetime import datetime
from tkinter import font as tkfont
import colorsys
import math

# [Previous AnimationEffects and ColorUtils classes remain the same]

class SingerConfigFrame(ttk.LabelFrame):
    def __init__(self, parent, singer_id, initial_color='#FF0000', callback=None):
        super().__init__(parent, text=f"Singer {singer_id}")
        self.singer_id = singer_id
        self.callback = callback
        
        # Singer name
        ttk.Label(self, text="Name:").grid(row=0, column=0, padx=5, pady=5)
        self.name_var = tk.StringVar(value=f"Singer {singer_id}")
        self.name_entry = ttk.Entry(self, textvariable=self.name_var)
        self.name_entry.grid(row=0, column=1, padx=5, pady=5)
        
        # Singer color
        self.color = initial_color
        self.color_btn = ttk.Button(self, text="Choose Color", command=self.choose_color)
        self.color_btn.grid(row=0, column=2, padx=5, pady=5)
        
        self.color_preview = tk.Label(self, text="■", fg=initial_color, font=('Arial', 20))
        self.color_preview.grid(row=0, column=3, padx=5, pady=5)
        
        # Active/Inactive toggle
        self.active_var = tk.BooleanVar(value=True)
        self.active_check = ttk.Checkbutton(self, text="Active", variable=self.active_var)
        self.active_check.grid(row=0, column=4, padx=5, pady=5)
        
    def choose_color(self):
        color = colorchooser.askcolor(color=self.color)[1]
        if color:
            self.color = color
            self.color_preview.configure(fg=color)
            if self.callback:
                self.callback(self.singer_id, color)
    
    def get_config(self):
        return {
            'id': self.singer_id,
            'name': self.name_var.get(),
            'color': self.color,
            'active': self.active_var.get()
        }

class MultiSingerLyricInput(ttk.Frame):
    def __init__(self, parent, num_singers=2):
        super().__init__(parent)
        self.num_singers = num_singers
        self.lyrics_texts = []
        
        # Create input areas for each singer
        for i in range(num_singers):
            frame = ttk.LabelFrame(self, text=f"Singer {i+1} Lyrics")
            frame.grid(row=0, column=i, padx=5, pady=5, sticky='nsew')
            
            text = scrolledtext.ScrolledText(frame, width=30, height=10)
            text.pack(padx=5, pady=5, fill=tk.BOTH, expand=True)
            self.lyrics_texts.append(text)
        
        self.grid_columnconfigure(tuple(range(num_singers)), weight=1)
    
    def get_lyrics(self):
        return [text.get('1.0', tk.END).strip().split('\n') for text in self.lyrics_texts]

class MultiSingerPreviewFrame(ttk.Frame):
    def __init__(self, parent, num_singers=2):
        super().__init__(parent)
        self.canvas = tk.Canvas(self, height=200, width=500, bg='white')
        self.canvas.pack(padx=5, pady=5, fill=tk.BOTH, expand=True)
        
        self.singer_configs = {}
        self.animation_config = {
            'effect': 'fade',
            'speed': 1.0,
            'easing': 'linear'
        }
    
    def update_singer_config(self, singer_id, config):
        self.singer_configs[singer_id] = config
    
    def update_preview(self, texts_and_progress):
        """
        texts_and_progress: list of tuples (text, progress, singer_config)
        """
        self.canvas.delete('all')
        
        width = self.canvas.winfo_width()
        height = self.canvas.winfo_height()
        
        # Calculate vertical spacing for multiple singers
        spacing = height / (len(texts_and_progress) + 1)
        
        for i, (text, progress, singer_config) in enumerate(texts_and_progress):
            y_pos = spacing * (i + 1)
            self.render_text(text, progress, singer_config, width, y_pos)
    
    def render_text(self, text, progress, singer_config, width, y_pos):
        effect = self.animation_config['effect']
        easing = getattr(AnimationEffects, self.animation_config['easing'])
        eased_progress = easing(progress)
        color = singer_config['color']
        
        if effect == 'fade':
            opacity = int(eased_progress * 255)
            text_color = ColorUtils.interpolate_color('#FFFFFF', color, eased_progress)
            self.canvas.create_text(width/2, y_pos, text=text, fill=text_color, font=('Arial', 24))
        # [Other effects implementation remains similar but adjusted for y_pos]

class EnhancedLyricTimingTool:
    def __init__(self, root):
        self.root = root
        self.root.title("Multi-Singer Lyrics Timing Tool")
        
        self.num_singers = 2
        self.singers = {}
        self.current_lines = [0] * self.num_singers
        self.timestamps = [[] for _ in range(self.num_singers)]
        
        self.setup_ui()
    
    def setup_ui(self):
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky='nsew')
        
        # Singer configuration section
        singers_frame = ttk.LabelFrame(main_frame, text="Singers Configuration")
        singers_frame.grid(row=0, column=0, pady=5, sticky='ew')
        
        colors = ['#FF0000', '#0000FF']  # Default colors for singers
        for i in range(self.num_singers):
            singer_config = SingerConfigFrame(
                singers_frame, 
                i+1, 
                initial_color=colors[i],
                callback=self.update_singer_config
            )
            singer_config.grid(row=0, column=i, padx=5, pady=5)
            self.singers[i+1] = singer_config
        
        # Animation configuration
        self.animation_config = AnimationConfigFrame(main_frame, self.update_animation_config)
        self.animation_config.grid(row=1, column=0, pady=5, sticky='ew')
        
        # Lyrics input
        self.lyrics_input = MultiSingerLyricInput(main_frame, self.num_singers)
        self.lyrics_input.grid(row=2, column=0, pady=5, sticky='ew')
        
        # Preview
        preview_frame = ttk.LabelFrame(main_frame, text="Live Preview")
        preview_frame.grid(row=3, column=0, pady=5, sticky='ew')
        self.preview = MultiSingerPreviewFrame(preview_frame, self.num_singers)
        self.preview.pack(fill=tk.BOTH, expand=True)
        
        # Controls
        controls_frame = ttk.Frame(main_frame)
        controls_frame.grid(row=4, column=0, pady=10)
        
        # Timer display
        self.timer_var = tk.StringVar(value="00:00.000")
        timer_label = ttk.Label(controls_frame, textvariable=self.timer_var, font=('Courier', 20))
        timer_label.grid(row=0, column=0, columnspan=4, pady=10)
        
        # Control buttons
        self.start_button = ttk.Button(controls_frame, text="Start", command=self.start_timing)
        self.start_button.grid(row=1, column=0, padx=5)
        
        # Mark buttons for each singer
        self.mark_buttons = []
        for i in range(self.num_singers):
            btn = ttk.Button(
                controls_frame,
                text=f"Mark Singer {i+1}",
                command=lambda x=i: self.mark_timestamp(x),
                state='disabled'
            )
            btn.grid(row=1, column=i+1, padx=5)
            self.mark_buttons.append(btn)
        
        self.stop_button = ttk.Button(controls_frame, text="Stop", command=self.stop_timing, state='disabled')
        self.stop_button.grid(row=1, column=len(self.mark_buttons)+1, padx=5)
        
        # Results display
        results_frame = ttk.Frame(main_frame)
        results_frame.grid(row=5, column=0, pady=5, sticky='ew')
        
        self.results_texts = []
        for i in range(self.num_singers):
            frame = ttk.LabelFrame(results_frame, text=f"Singer {i+1} Timing Results")
            frame.grid(row=0, column=i, padx=5, pady=5, sticky='nsew')
            
            text = scrolledtext.ScrolledText(frame, width=30, height=10)
            text.pack(padx=5, pady=5, fill=tk.BOTH, expand=True)
            self.results_texts.append(text)
        
        # Export button
        ttk.Button(main_frame, text="Export", command=self.export_timestamps).grid(row=6, column=0, pady=10)
    
    def start_timing(self):
        self.lyrics = self.lyrics_input.get_lyrics()
        if not all(lyrics and lyrics[0] for lyrics in self.lyrics):
            return
        
        self.start_time = time.time()
        self.is_running = True
        self.current_lines = [0] * self.num_singers
        self.timestamps = [[] for _ in range(self.num_singers)]
        
        self.start_button.config(state='disabled')
        for btn in self.mark_buttons:
            btn.config(state='normal')
        self.stop_button.config(state='normal')
        
        self.update_timer()
        self.update_preview()
    
    def mark_timestamp(self, singer_idx):
        if not self.is_running:
            return
        
        current_time = time.time() - self.start_time
        if self.current_lines[singer_idx] < len(self.lyrics[singer_idx]):
            self.timestamps[singer_idx].append({
                'time': current_time,
                'text': self.lyrics[singer_idx][self.current_lines[singer_idx]],
                'singer_config': self.singers[singer_idx + 1].get_config()
            })
            self.current_lines[singer_idx] += 1
            self.update_results()
        
        if all(cl >= len(lyrics) for cl, lyrics in zip(self.current_lines, self.lyrics)):
            self.stop_timing()
    
    def stop_timing(self):
        self.is_running = False
        self.start_button.config(state='normal')
        for btn in self.mark_buttons:
            btn.config(state='disabled')
        self.stop_button.config(state='disabled')
    
    def update_timer(self):
        if self.is_running:
            elapsed = time.time() - self.start_time
            minutes = int(elapsed // 60)
            seconds = elapsed % 60
            self.timer_var.set(f"{minutes:02d}:{seconds:06.3f}")
            self.root.after(10, self.update_timer)
    
    def update_preview(self):
        if self.is_running:
            elapsed = time.time() - self.start_time
            preview_data = []
            
            for singer_idx in range(self.num_singers):
                if self.current_lines[singer_idx] < len(self.lyrics[singer_idx]):
                    text = self.lyrics[singer_idx][self.current_lines[singer_idx]]
                    progress = (elapsed % 1.0)
                    singer_config = self.singers[singer_idx + 1].get_config()
                    preview_data.append((text, progress, singer_config))
            
            self.preview.update_preview(preview_data)
            self.root.after(16, self.update_preview)
    
    def update_results(self):
        for singer_idx, (timestamps, text) in enumerate(zip(self.timestamps, self.results_texts)):
            text.delete('1.0', tk.END)
            for ts in timestamps:
                minutes = int(ts['time'] // 60)
                seconds = ts['time'] % 60
                text.insert(tk.END, f"{minutes:02d}:{seconds:06.3f} - {ts['text']}\n")
    
    def export_timestamps(self):
        if not any(self.timestamps):
            return
        
        export_data = {
            'timestamps': self.timestamps,
            'singer_configs': {i: singer.get_config() for i, singer in self.singers.items()},
            'animation_config': self.preview.animation_config
        }
        
        filename = f"multi_singer_timing_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(filename, 'w') as f:
            json.dump(export_data, f, indent=2)

def main():
    root = tk.Tk()
    app = EnhancedLyricTimingTool(root)
    root.mainloop()

if __name__ == "__main__":
    main()