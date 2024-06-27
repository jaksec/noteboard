import tkinter as tk
from tkinter import font, messagebox
from PIL import Image, ImageTk
import json

# initial tk window
w = tk.Tk()
w.resizable(False, False)
w.title("Noteboard")
w.geometry("920x700")
container = tk.Frame(w)
container.pack(fill="both", expand=True)

# Initialize control mappings with all notes unbound
control_mappings = {note: None for note in ["Note C", "Note D", "Note E", "Note F", "Note G", "Note A", "Note B"]}

# Load existing control mappings from file
def load_control_mappings():
    global control_mappings
    try:
        with open("config.json", "r") as file:
            control_mappings = json.load(file)
    except FileNotFoundError:
        # If file doesn't exist, initialize with all notes unbound
        control_mappings = {note: None for note in ["Note C", "Note D", "Note E", "Note F", "Note G", "Note A", "Note B"]}

# Save control mappings to file
def save_control_mappings():
    with open("config.json", "w") as file:
        json.dump(control_mappings, file)

# Function to update control mappings and save to file
def update_control_mapping(note, key):
    # Check if the key is already used
    if key in control_mappings.values() and control_mappings[note] != key:
        # Ask for confirmation to replace existing mapping
        confirm_replace = messagebox.askyesno("Replace Key",
            f"The key '{key}' is already mapped to another note.\nDo you want to replace it?")
        if not confirm_replace:
            return
    
    # Unbind any existing note that uses this key
    for existing_note, existing_key in list(control_mappings.items()):
        if existing_key == key:
            control_mappings[existing_note] = None
    
    control_mappings[note] = key if key != "None" else None  # Set to None if unbinding
    save_control_mappings()
    update_mappings_display()

# Function to remove a key binding
def unbind_key(key):
    for note, bound_key in list(control_mappings.items()):
        if bound_key == key:
            control_mappings[note] = None
    save_control_mappings()
    update_mappings_display()

load_control_mappings()

# functions and classes
class AnimatedGifLabel(tk.Label):
    def __init__(self, master, gif_path, bg_color):
        super().__init__(master, bg=bg_color)
        self.gif_path = gif_path
        self.frames = self.load_gif_frames()
        self.current_frame = 0
        self.display_frame()

    def load_gif_frames(self):
        gif = Image.open(self.gif_path)
        frames = []
        try:
            while True:
                frames.append(ImageTk.PhotoImage(gif.copy()))
                gif.seek(len(frames))
        except EOFError:
            pass
        return frames

    def display_frame(self):
        self.config(image=self.frames[self.current_frame])
        self.current_frame = (self.current_frame + 1) % len(self.frames)
        self.after(20, self.display_frame)  # Adjust the delay for animation

    def reset_animation(self):
        self.current_frame = 0

# action functions
def show_frame(frame):
    frame.tkraise()

def show_animation():
    gif_label.reset_animation()
    gif_label.place(x=303, y=406)

def hide_gif():
    gif_label.place_forget()

def back_b_commands():
    key_label.config(text="")
    show_frame(main_frame)

# Function to handle mapping mouse actions
def map_mouse_action():
    note = selected_note.get()
    action = selected_mouse_action.get()
    key_label.place(y=400, x=330)
    key_label.config(text=f"Mapped: {note} -> {action}")
    update_control_mapping(note, action)

# Function to display current mappings
def update_mappings_display():
    mappings_text.config(state=tk.NORMAL)  # Enable editing
    mappings_text.delete(1.0, tk.END)  # Clear previous mappings
    for note, key in control_mappings.items():
        mappings_text.insert(tk.END, f"{note} -> {key if key else 'Unbound'}\n")
    mappings_text.config(state=tk.DISABLED)  # Disable editing

# Function to handle mapping
def map_note_to_key():
    note = selected_note.get()
    key_label.place(y=400, x=390)
    key_label.config(text="Press any key...")
    
    # Capture key press event and map it to the selected note
    def on_key_press(event):
        key = event.keysym.upper()
        if control_mappings.get(note) == key:
            key_label.place(y=400, x=330)
            key_label.config(text=f"{key} is already mapped to {note}.")
        else:
            key_label.place(y=400, x=365)
            key_label.config(text=f"Mapped: {note} -> {key}")
            update_control_mapping(note, key)
        w.focus_set()  # Return focus to the main window after mapping
        w.unbind("<Key>")  # Unbind to prevent multiple mappings with a single key press
    
    w.bind("<Key>", on_key_press)

def unbind_key(note):
    key_label.place(y=400, x=385)
    key_label.config(text=f"{note} unbinded.")
    control_mappings[note] = None
    update_mappings_display()

# frames for application
main_frame = tk.Frame(container, bg='lightblue')
control_frame = tk.Frame(container, bg='lightgreen')

# image preprocessing
gif_label = AnimatedGifLabel(main_frame, 'img/red-circle-blink.gif', 'lightblue')

# fonts and miscellaneous
cool_font = font.Font(family="Comic Sans MS", size=26, weight="bold")
other = font.Font(family="Arial", size=13)
other1 = font.Font(family="Arial", size=13, weight="bold") #fix this

# main frame content
welcome = tk.Label(main_frame, text="Welcome to Noteboard!", font=cool_font, bg='lightblue')
welcome.pack(pady=20)
description = tk.Label(main_frame, text="A tool for translating music notes into key presses.", font=other, bg='lightblue')
description.pack(pady=40)
copyrighted = tk.Label(main_frame, text="Copyright © 2024 Chris Jaksec. All rights reserved.", font=other, bg='lightblue')
copyrighted.place(x=510, y=670)
    # buttons in main frame
control_b = tk.Button(main_frame, text="Controls", command=lambda: show_frame(control_frame))
begin_b = tk.Button(main_frame, text="Start Recording", command=show_animation)
end_b = tk.Button(main_frame, text="End", command=hide_gif)

# Control mapping label
key_label = tk.Label(control_frame, text="", font=other1, bg='lightgreen')

# control frame content

    # display for controls
mappings_label = tk.Label(control_frame, text="Current Mappings:", font=cool_font, bg='lightgreen')
mappings_label.pack(pady=20)
mappings_text = tk.Text(control_frame, width=40, height=10, font=other)
mappings_text.pack()
update_mappings_display()
    # title
title = tk.Label(control_frame, text="Control Menu", font=cool_font, bg='lightgreen')
title.pack(pady=40)

    # Dropdown menu for control mappings (notes)
notes = ["Note C", "Note D", "Note E", "Note F", "Note G", "Note A", "Note B"]
selected_note = tk.StringVar(control_frame)
selected_note.set(notes[0])  # Default to first note

    # Drop down menu for mouse controls
mouse_options = ["MOUSE_UP", "MOUSE_DOWN", "MOUSE_LEFT", "MOUSE_RIGHT"]
selected_mouse_action = tk.StringVar(control_frame)
selected_mouse_action.set(mouse_options[0])  # Default to first option


    # buttons and drop downs
back_b = tk.Button(control_frame, text="Back", command=back_b_commands)
unbind_button = tk.Button(control_frame, text="Unbind", command=lambda: unbind_key(selected_note.get()))
note_dropdown = tk.OptionMenu(control_frame, selected_note, *notes)
map_button = tk.Button(control_frame, text="Map Note to Key", command=map_note_to_key)
map_mouse_button = tk.Button(control_frame, text="Map Note to Mouse Action", command=map_mouse_action)
mouse_dropdown = tk.OptionMenu(control_frame, selected_mouse_action, *mouse_options)
map_mouse_button = tk.Button(control_frame, text="Map Note to Mouse Action", command=map_mouse_action)
mouse_dropdown = tk.OptionMenu(control_frame, selected_mouse_action, *mouse_options)
    
# placements
control_b.place(x=500, y=400)
begin_b.place(x=320, y=400)
end_b.place(x=420, y=400)
back_b.place(x=600, y=600)
unbind_button.place(x=370, y=535)
mouse_dropdown.place(y=530, x=480)
map_button.place(x=340, y=500)
map_mouse_button.place(x=460, y=500)
note_dropdown.pack(pady=20)

# loop for frames
for frame in (main_frame, control_frame):
    frame.place(x=0, y=0, width=900, height=720)
show_frame(main_frame)

def on_close():
    save_control_mappings()
    w.destroy()

# main
w.protocol("WM_DELETE_WINDOW", on_close)
w.mainloop()
