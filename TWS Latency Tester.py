import tkinter as tk
from tkinter import messagebox
import pygame
import threading
import time
import numpy as np

class BeatPlayer:
    def __init__(self, master):
        self.master = master
        self.master.title("Latency Tester")
        pygame.mixer.init()
        self.sound = self.generate_beep()
        tk.Label(master, text="BPM:").grid(row=0, column=0, sticky="e")
        self.bpm_entry = tk.Entry(master)
        self.bpm_entry.grid(row=0, column=1)
        self.bpm_entry.insert(0, "120")
        tk.Label(master, text="Latency(ms):").grid(row=1, column=0, sticky="e")
        self.latency_entry = tk.Entry(master)
        self.latency_entry.grid(row=1, column=1)
        self.latency_entry.insert(0, "0")
        self.play_btn = tk.Button(master, text="Play", command=self.start_beat)
        self.play_btn.grid(row=2, column=0)
        self.stop_btn = tk.Button(master, text="Stop", command=self.stop_beat, state=tk.DISABLED)
        self.stop_btn.grid(row=2, column=1)
        self.canvas = tk.Canvas(master, width=800, height=800)
        self.canvas.grid(row=3, column=0, columnspan=2, pady=10)
        self.rect = self.canvas.create_rectangle(0, 0, 800, 800, fill="black")
        self.playing = False
        self.thread = None

    def generate_beep(self):
        frequency = 440
        sample_rate = 44100
        duration = 0.1
        t = np.linspace(0, duration, int(sample_rate * duration), False)
        wave = 0.5 * np.sin(2 * np.pi * frequency * t)
        audio = np.array(wave * 32767, dtype=np.int16)
        stereo_sound = np.column_stack((audio, audio))
        return pygame.sndarray.make_sound(stereo_sound)

    def start_beat(self):
        if self.playing:
            return

        self.playing = True
        self.play_btn.config(state=tk.DISABLED)
        self.stop_btn.config(state=tk.NORMAL)
        self.thread = threading.Thread(target=self.run_beat, daemon=True)
        self.thread.start()

    def run_beat(self):
        while self.playing:
            try:
                bpm = float(self.bpm_entry.get())
                latency = float(self.latency_entry.get()) / 1000
                if bpm <= 0 or latency < 0:
                    raise ValueError
            except ValueError:
                time.sleep(0.1)
                continue

            beat_interval = 60.0 / bpm
            start_time = time.time()
            pygame.mixer.Sound.play(self.sound)
            threading.Thread(target=self.delayed_flash, args=(latency,), daemon=True).start()
            elapsed = time.time() - start_time
            sleep_time = beat_interval - elapsed
            
            if sleep_time > 0:
                time.sleep(sleep_time)

    def delayed_flash(self, latency):
        time.sleep(latency)
        self.canvas.itemconfig(self.rect, fill="white")
        self.master.update_idletasks()
        time.sleep(0.1)
        self.canvas.itemconfig(self.rect, fill="black")
        self.master.update_idletasks()

    def stop_beat(self):
        self.playing = False
        self.play_btn.config(state=tk.NORMAL)
        self.stop_btn.config(state=tk.DISABLED)

if __name__ == "__main__":
    root = tk.Tk()
    app = BeatPlayer(root)
    root.mainloop()
