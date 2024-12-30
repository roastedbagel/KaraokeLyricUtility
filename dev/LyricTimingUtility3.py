import tkinter as tk
from tkinter import ttk, scrolledtext, colorchooser
import time
import json
from datetime import datetime
from tkinter import font as tkfont
import colorsys

class AnimationEffects:
    @staticmethod
    def linear(progress):
        return progress
    
    @staticmethod
    def ease_in(progress):
        return progress * progress
    
    @staticmethod
    def ease_out(progress):
        return -(progress - 1) * (progress - 1) + 1
    
    @staticmethod
    def ease_in_out(progress):
        if progress < 0.5:
            return 2 * progress * progress
        return (-2 * progress * progress) + (4 * progress) - 1
    
    @staticmethod
    def bounce(progress):
        bounce = 4
        return abs(math.sin(progress * math.pi * bounce))

class ColorUtils:
    @staticmethod
    def interpolate_color(start_color, end_color, progress):
        """Interpolate between two colors using HSV color space"""
        # Convert hex to RGB
        start_rgb = tuple(int(start_color[i:i+2], 16) for i in (1, 3, 5))
        end_rgb = tuple(int(end_color[i:i+2], 16) for i in (1, 3, 5))
        
        # Convert RGB to HSV
        start_hsv = colorsys.rgb_to_hsv(*[x/255 for x in start_rgb])
        end_hsv = colorsys.rgb_to_hsv(*[x/255 for x in end_rgb])
        
        # Interpolate in HSV space
        h = start_hsv[0] + (end_hsv[0] - start_hsv[0]) * progress
        s = start_hsv[1] + (end_hsv[1] - start_hsv[1]) * progress
        v = start_hsv[2] + (end_hsv[2] - start_hsv[2]) * progress
        
        # Convert back to RGB
        rgb = colorsys.hsv_to_rgb(h, s, v)
        
        # Convert to hex
        return f'#{int(rgb[0]*255):02x}{int(rgb[1]*255):02x}{int(rgb[2]*255):02x}'

class AnimationConfigFrame(ttk.LabelFrame):
    def __init__(self, parent, callback):
        super().__init__(parent, text="Animation Configuration")
        self.callback = callback
        
        # Animation type
        ttk.Label(self, text="Effect:").grid(row=0, column=0, padx=5, pady=5)
        self.effect_var = tk.StringVar(value="fade")
        effects = ttk.Combobox(self, textvariable=self.effect_var, values=[
            "fade", "slide", "typewriter", "wave", "rainbow", "pulse"
        ])
        effects.grid(row=0, column=1, padx=5)
        
        # Animation speed
        ttk.Label(self, text="Speed:").grid(row=0, column=2, padx=5, pady=5)
        self.speed_var = tk.DoubleVar(value=1.0)
        speed = ttk.Scale(self, from_=0.1, to=2.0, variable=self.speed_var, orient=tk.HORIZONTAL)
        speed.grid(row=0, column=3, padx=5)
        
        # Easing function
        ttk.Label(self, text="Easing:").grid(row=1, column=0, padx=5, pady=5)
        self.easing_var = tk.StringVar(value="linear")
        easing = ttk.Combobox(self, textvariable=self.easing_var, values=[
            "linear", "ease_in", "ease_out", "ease_in_out", "bounce"
        ])
        easing.grid(row=1, column=1, padx=5)
        
        # Update button
        ttk.Button(self, text="Apply", command=self.update_animation).grid(row=1, column=3, padx=5)
        
    def update_animation(self):
        self.callback({
            'effect': self.effect_var.get(),
            'speed': self.speed_var.get(),
            'easing': self.easing_var.get()
        })

class EnhancedLyricPreviewFrame(ttk.Frame):
    def __init__(self, parent):
        super().__init__(parent)
        self.canvas = tk.Canvas(self, height=100, width=500, bg='white')
        self.canvas.pack(padx=5, pady=5, fill=tk.BOTH, expand=True)
        
        self.animation_config = {
            'effect': 'fade',
            'speed': 1.0,
            'easing': 'linear'
        }
        
        self.text_id = None
        self.animation_frame = 0
        
    def set_animation_config(self, config):
        self.animation_config = config
        
    def update_preview(self, text, progress=0):
        self.canvas.delete('all')
        
        # Get dimensions
        width = self.canvas.winfo_width()
        height = self.canvas.winfo_height()
        
        effect = self.animation_config['effect']
        speed = self.animation_config['speed']
        easing = getattr(AnimationEffects, self.animation_config['easing'])
        
        # Apply easing function to progress
        eased_progress = easing(progress)
        
        if effect == 'fade':
            # Fade effect
            opacity = int(eased_progress * 255)
            color = f'#{opacity:02x}{opacity:02x}{opacity:02x}'
            self.canvas.create_text(width/2, height/2, text=text, fill=color, font=('Arial', 24))
            
        elif effect == 'slide':
            # Slide effect
            x_pos = width * (eased_progress - 1)
            self.canvas.create_text(x_pos, height/2, text=text, fill='black', font=('Arial', 24))
            
        elif effect == 'typewriter':
            # Typewriter effect
            chars_to_show = int(len(text) * eased_progress)
            display_text = text[:chars_to_show]
            self.canvas.create_text(width/2, height/2, text=display_text, fill='black', font=('Arial', 24))
            
        elif effect == 'wave':
            # Wave effect
            for i, char in enumerate(text):
                phase = (i / len(text) + progress) * 2 * math.pi
                y_offset = math.sin(phase) * 20
                self.canvas.create_text(
                    width/2 - (len(text)*10)/2 + i*20,
                    height/2 + y_offset,
                    text=char,
                    fill='black',
                    font=('Arial', 24)
                )
                
        elif effect == 'rainbow':
            # Rainbow effect
            for i, char in enumerate(text):
                hue = (i / len(text) + progress) % 1.0
                rgb = colorsys.hsv_to_rgb(hue, 1.0, 1.0)
                color = f'#{int(rgb[0]*255):02x}{int(rgb[1]*255):02x}{int(rgb[2]*255):02x}'
                self.canvas.create_text(
                    width/2 - (len(text)*10)/2 + i*20,
                    height/2,
                    text=char,
                    fill=color,
                    font=('Arial', 24)
                )
                
        elif effect == 'pulse':
            # Pulse effect
            scale = 1 + math.sin(progress * 2 * math.pi) * 0.2
            font = ('Arial', int(24 * scale))
            self.canvas.create_text(width/2, height/2, text=text, fill='black', font=font)

class LyricTimingTool:
    # ... (previous code remains the same until setup_ui)
    
    def setup_ui(self):
        # ... (previous setup_ui code remains the same until preview section)
        
        # Add animation configuration
        self.animation_config = AnimationConfigFrame(main_frame, self.update_animation_config)
        self.animation_config.grid(row=2, column=0, pady=5, sticky=(tk.W, tk.E))
        
        # Update preview section to use enhanced preview
        preview_frame = ttk.LabelFrame(main_frame, text="Live Preview")
        preview_frame.grid(row=3, column=0, pady=5, sticky=(tk.W, tk.E))
        self.preview = EnhancedLyricPreviewFrame(preview_frame)
        self.preview.pack(fill=tk.X, padx=5, pady=5)
        
        # ... (rest of setup_ui code remains the same)
    
    def update_animation_config(self, config):
        self.preview.set_animation_config(config)
        
    def update_preview_text(self):
        if self.current_line < len(self.lyrics):
            elapsed = (time.time() - self.start_time) % (2.0 / self.preview.animation_config['speed'])
            progress = elapsed / (2.0 / self.preview.animation_config['speed'])
            self.preview.update_preview(self.lyrics[self.current_line], progress)
            self.root.after(16, self.update_preview_text)  # ~60 FPS animation

# ... (rest of the code remains the same)