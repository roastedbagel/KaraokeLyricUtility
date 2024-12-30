import tkinter as tk
from tkinter import ttk, scrolledtext
import time
import json
from datetime import datetime

class LyricTimingTool:
    def __init__(self, root):
        self.root = root
        self.root.title("Lyrics Timing Tool")
        
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
        
        # Lyrics input
        ttk.Label(main_frame, text="Enter lyrics (one line per row):").grid(row=0, column=0, pady=5)
        self.lyrics_text = scrolledtext.ScrolledText(main_frame, width=50, height=10)
        self.lyrics_text.grid(row=1, column=0, pady=5)
        
        # Controls frame
        controls_frame = ttk.Frame(main_frame)
        controls_frame.grid(row=2, column=0, pady=10)
        
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
        
        # Current line display
        self.current_line_var = tk.StringVar(value="Ready to start...")
        ttk.Label(main_frame, textvariable=self.current_line_var).grid(row=3, column=0, pady=5)
        
        # Results display
        ttk.Label(main_frame, text="Timing Results:").grid(row=4, column=0, pady=5)
        self.results_text = scrolledtext.ScrolledText(main_frame, width=50, height=10)
        self.results_text.grid(row=5, column=0, pady=5)
        
        # Export button
        ttk.Button(main_frame, text="Export Timestamps", command=self.export_timestamps).grid(row=6, column=0, pady=10)
        
    def start_timing(self):
        self.lyrics = self.lyrics_text.get('1.0', tk.END).strip().split('\n')
        if not self.lyrics or self.lyrics[0] == '':
            self.current_line_var.set("Please enter lyrics first!")
            return
            
        self.start_time = time.time()
        self.is_running = True
        self.current_line = 0
        self.timestamps = []
        
        self.start_button.config(state='disabled')
        self.mark_button.config(state='normal')
        self.stop_button.config(state='normal')
        self.update_timer()
        self.update_current_line()
        
    def mark_timestamp(self):
        if not self.is_running:
            return
            
        current_time = time.time() - self.start_time
        if self.current_line < len(self.lyrics):
            self.timestamps.append({
                'time': current_time,
                'text': self.lyrics[self.current_line]
            })
            self.current_line += 1
            self.update_current_line()
            self.update_results()
            
        if self.current_line >= len(self.lyrics):
            self.stop_timing()
            
    def stop_timing(self):
        self.is_running = False
        self.start_button.config(state='normal')
        self.mark_button.config(state='disabled')
        self.stop_button.config(state='disabled')
        self.current_line_var.set("Timing complete!")
        
    def update_timer(self):
        if self.is_running:
            elapsed = time.time() - self.start_time
            minutes = int(elapsed // 60)
            seconds = elapsed % 60
            self.timer_var.set(f"{minutes:02d}:{seconds:06.3f}")
            self.root.after(10, self.update_timer)
            
    def update_current_line(self):
        if self.current_line < len(self.lyrics):
            self.current_line_var.set(f"Current line: {self.lyrics[self.current_line]}")
        else:
            self.current_line_var.set("All lines complete!")
            
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
            json.dump(self.timestamps, f, indent=2)
        self.current_line_var.set(f"Exported to {filename}")

def main():
    root = tk.Tk()
    app = LyricTimingTool(root)
    root.mainloop()

if __name__ == "__main__":
    main()