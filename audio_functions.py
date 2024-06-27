import pyautogui
import numpy as np
import pyaudio
import json

def save_controls(controls, filename="config.json"):
    with open(filename, 'w') as f:
        json.dump(controls, f)

def load_controls(filename="config.json"):
    try:
        with open(filename, 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        return {}
