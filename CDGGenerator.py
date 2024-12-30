class CDGGenerator:
    def __init__(self):
        # CD+G commands
        self.CMD_MEMORY_PRESET = 0x01
        self.CMD_BORDER_PRESET = 0x02
        self.CMD_TILE_BLOCK = 0x06
        self.CMD_SCROLL_PRESET = 0x14
        self.CMD_LOAD_CLUT = 0x1F
        self.CMD_TEXT_DISPLAY = 0x09
        
        # Standard CD+G dimensions (300x216 pixels)
        self.WIDTH = 300
        self.HEIGHT = 216
        
        # Packets are generated at 300 packets per second
        self.PACKETS_PER_SECOND = 300
        
    def create_packet(self, instruction, data):
        """Create a single CD+G packet"""
        command = bytes([0x09, 0x63, 0x67, 0x00])  # Standard CD+G command
        packet_data = data[:16].ljust(16, b'\x00')
        parity = self._calculate_parity(instruction, packet_data)
        return command + bytes([instruction]) + packet_data + parity
    
    def _calculate_parity(self, instruction, data):
        """Calculate parity bytes for error checking"""
        # In a real implementation, this would be more complex
        # This is a simplified version for demonstration
        return bytes([0x00, 0x00, 0x00])
    
    def _encode_text(self, text):
        """Convert text to CD+G compatible format"""
        # CD+G can only display uppercase ASCII
        return text.upper().encode('ascii', errors='replace')[:16]
    
    def generate_timing_packet(self, timestamp_ms):
        """Generate a timing marker packet"""
        # Convert milliseconds to packet number
        packet_num = int(timestamp_ms * self.PACKETS_PER_SECOND / 1000)
        timing_data = packet_num.to_bytes(4, 'big') + bytes([0x00] * 12)
        return self.create_packet(self.CMD_TEXT_DISPLAY, timing_data)
    
    def generate_lyrics_file(self, lyrics_data):
        """
        Generate CD+G packets for lyrics
        lyrics_data: List of tuples (timestamp_ms, lyric_text)
        """
        packets = []
        
        # Initialize display
        packets.append(self.create_packet(
            self.CMD_MEMORY_PRESET,
            bytes([0x00] * 16)  # Clear screen
        ))
        
        # Set up color palette
        color_table = bytes([
            0x00, 0x00,  # Background (Black)
            0xFF, 0xFF,  # Foreground (White)
            0x00, 0x00, 0x00, 0x00,  # Unused colors
            0x00, 0x00, 0x00, 0x00,
            0x00, 0x00, 0x00, 0x00
        ])
        packets.append(self.create_packet(self.CMD_LOAD_CLUT, color_table))
        
        # Generate lyrics packets
        for timestamp, text in sorted(lyrics_data):
            # Add timing marker
            packets.append(self.generate_timing_packet(timestamp))
            
            # Add text display packets
            text_bytes = self._encode_text(text)
            packets.append(self.create_packet(self.CMD_TEXT_DISPLAY, text_bytes))
        
        return packets

    def save_to_file(self, packets, filename):
        """Save packets to binary file"""
        with open(filename, 'wb') as f:
            for packet in packets:
                f.write(packet)

# Example usage:
def create_example_lyrics_file():
    generator = CDGGenerator()
    
    # Example lyrics with timestamps (in milliseconds)
    lyrics = [
        (0, "WELCOME TO KARAOKE"),
        (2000, "SING ALONG WITH ME"),
        (4000, "FOLLOW THE BOUNCING BALL"),
        (6000, "LET'S BEGIN..."),
    ]
    
    packets = generator.generate_lyrics_file(lyrics)
    generator.save_to_file(packets, "example_lyrics.cdg")
    
    return len(packets), "example_lyrics.cdg"