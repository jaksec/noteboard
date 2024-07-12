import pyaudio
import numpy as np
import aubio
import json
import os
import time
from pynput.keyboard import Controller as KeyboardController
from pynput.mouse import Button, Controller as MouseController

# Load control mappings from file
def load_control_mappings():
    if os.path.exists("config.json"):
        with open("config.json", "r") as file:
            return json.load(file)
    return {note: None for note in ["Note C", "Note D", "Note E", "Note F", "Note G", "Note A", "Note B"]}

control_mappings = load_control_mappings()

# Initialize the audio stream and pitch detection
p = pyaudio.PyAudio()

# Constants for the audio stream
BUFFER_SIZE = 1024
FORMAT = pyaudio.paFloat32
CHANNELS = 1
RATE = 44100

stream = p.open(format=FORMAT,
                channels=CHANNELS,
                rate=RATE,
                input=True,
                frames_per_buffer=BUFFER_SIZE)

# Aubio's pitch detection
tolerance = 0.8
win_s = 4096  # FFT size
hop_s = BUFFER_SIZE  # Hop size
pitch_o = aubio.pitch("default", win_s, hop_s, RATE)
pitch_o.set_unit("Hz")
pitch_o.set_tolerance(tolerance)

# Notes frequency dictionary
notes_freqs = {
    "Note C": 261.63,
    "Note D": 293.66,
    "Note E": 329.63,
    "Note F": 349.23,
    "Note G": 392.00,
    "Note A": 440.00,
    "Note B": 493.88
}

# Helper function to match frequency to the closest note
def freq_to_note(freq):
    if freq == 0:
        return None
    note = min(notes_freqs, key=lambda x: abs(notes_freqs[x] - freq))
    return note

# Controllers for keyboard and mouse
keyboard = KeyboardController()
mouse = MouseController()

# Function to start processing audio
def start_recording():
    print("Recording started...")
    while True:
        try:
            data = stream.read(BUFFER_SIZE)
            samples = np.frombuffer(data, dtype=aubio.float_type)

            # Calculate the amplitude of the signal
            amplitude = np.sum(samples**2)/len(samples)
            if amplitude < 0.01:  # Adjust threshold as necessary
                continue  # Ignore low amplitude sounds

            pitch = pitch_o(samples)[0]
            note = freq_to_note(pitch)

            if note and control_mappings[note]:
                action = control_mappings[note]
                if action in ["MOUSE_UP", "MOUSE_DOWN", "MOUSE_LEFT", "MOUSE_RIGHT", "MOUSE_CLICK"]:
                    mouse_actions(action)
                else:
                    keyboard.press(action)
                    keyboard.release(action)
                    time.sleep(0.1)
        except KeyboardInterrupt:
            print("Recording stopped.")
            break

last_click_time = time.time()

def mouse_actions(action):
    global last_click_time
    x, y = mouse.position
    current_time = time.time()

    # Define cooldown period in seconds
    cooldown_period = 0.5  # Adjust this value as needed

    if action == "MOUSE_UP":
        mouse.position = (x, y - 10)
        time.sleep(0.025)
    elif action == "MOUSE_DOWN":
        mouse.position = (x, y + 10)
        time.sleep(0.025)
    elif action == "MOUSE_LEFT":
        mouse.position = (x - 10, y)
        time.sleep(0.025)
    elif action == "MOUSE_RIGHT":
        mouse.position = (x + 10, y)
        time.sleep(0.025)
    elif action == "MOUSE_CLICK":
        if current_time - last_click_time > cooldown_period:
            mouse.click(Button.left)
            last_click_time = current_time

if __name__ == "__main__":
    start_recording()

