import time
import tkinter as tk
from tkinter import ttk, messagebox
import wave
from PIL import Image, ImageTk
import pyodbc
import pypyodbc
import os
import pyaudio
import numpy as np
from faster_whisper import WhisperModel
import threading

# Define the path to your Access DB
db_path = os.path.abspath("contacts.mdb")
conn_str = f'Driver={{Microsoft Access Driver (*.mdb, *.accdb)}};DBQ={db_path};'
# Audio recording parameters
duration = 5  # seconds
fs = 44100    # sample rate
buffer = 1024

audio = pyaudio.PyAudio()
stream = audio.open(format=pyaudio.paInt16, channels=1, rate=fs, input=True, start=False, frames_per_buffer=buffer)
frames = []

def record_and_transcribe_faster():
    is_recording = True

    def record_loop():
        nonlocal is_recording
        try:
            while is_recording:
                data = stream.read(buffer)
                frames.append(data)
        except Exception as e:
            print("Recording error:", e)

    def stop_recording():
        nonlocal is_recording
        is_recording = False
        stream.stop_stream()
        stream.close()
        sound_file = wave.open("temp_voice.wav", 'wb')
        sound_file.setnchannels(1)
        sound_file.setsampwidth(audio.get_sample_size(pyaudio.paInt16))
        sound_file.setframerate(fs)
        sound_file.writeframes(b''.join(frames))
        sound_file.close()
        recording_modal.destroy()
        process_audio()

    def process_audio():
        # Show processing modal
        processing_modal = tk.Toplevel(root)
        processing_modal.title("Processing")
        processing_modal.geometry("300x100")
        processing_modal.configure(bg="white")
        processing_modal.grab_set()

        label = tk.Label(processing_modal, text="Processing voice input...", bg="white", font=("Segoe UI", 12))
        label.pack(pady=30)
        root.update()

        try:
            time.sleep(1)  # Simulate processing delay
            # model = WhisperModel("base", device="cpu", compute_type="int8")
            # segments, _ = model.transcribe("temp_voice.wav", language="en")
            # text = " ".join([segment.text for segment in segments]).strip()
            # parse_and_fill_fields(text)
        except Exception as e:
            messagebox.showerror("Voice Error", f"Failed to process voice:\n{e}")
        finally:
            processing_modal.destroy()

    # Show recording modal
    recording_modal = tk.Toplevel(root)
    recording_modal.title("Recording")
    recording_modal.geometry("300x150")
    recording_modal.configure(bg="white")
    recording_modal.grab_set()

    label = tk.Label(recording_modal, text="Recording now...\nPress OK to stop", bg="white", font=("Segoe UI", 12))
    label.pack(pady=20)

    ok_button = ttk.Button(recording_modal, text="OK", command=stop_recording)
    ok_button.pack()

    # Start recording in background thread
    stream.start_stream()
    frames.clear()
    threading.Thread(target=record_loop, daemon=True).start()

# Check if the file exists
if not os.path.exists(db_path):
    try:
        # Create a new Access database file
        pypyodbc.win_create_mdb(db_path)
        print("Database created successfully.")
    except Exception as e:
        print("Failed to create database:", e)
else:
    print("Database already exists.")

def save_data():
    val1 = entry1.get().strip()
    val2 = entry2.get().strip()

    if val1 == "" or val1 == "Name" or val2 == "" or val2 == "Address":
        messagebox.showwarning("Validation Error", "Both Name and Address are required.")
    else:
        try:
            conn = pyodbc.connect(conn_str)
            cursor = conn.cursor()

            # Try to create the table; ignore error if it already exists
            try:
                cursor.execute("""
                    CREATE TABLE contacts (
                        ID AUTOINCREMENT PRIMARY KEY,
                        Name TEXT(100),
                        Address TEXT(255)
                    )
                """)
            except Exception as e:
                if "already exists" in str(e):
                    pass  # Table already exists, no problem
                else:
                    raise  # Unexpected error, re-raise
            cursor.execute("INSERT INTO contacts (Name, Address) VALUES (?, ?)", (val1, val2))
            conn.commit()

            cursor.close()
            conn.close()

            print(f"Saved: {val1}, {val2}")
            messagebox.showinfo("Success", "Data saved successfully to database!")
        except Exception as e:
            messagebox.showerror("Database Error", f"Failed to save data:\n{e}")


def on_entry_click(entry, placeholder):
    if entry.get() == placeholder:
        entry.delete(0, "end")
        entry.config(foreground='black')

def on_focusout(entry, placeholder):
    if entry.get() == '':
        entry.insert(0, placeholder)
        entry.config(foreground='gray')

# Create main window
root = tk.Tk()
root.title("HY Infotech GUI")
root.geometry("640x480")
root.configure(bg="white")

# Load and display logo
logo_img = Image.open("logo.png")  # Replace with your logo file
logo_img = logo_img.resize((120, 120))
logo = ImageTk.PhotoImage(logo_img)

logo_label = tk.Label(root, image=logo, bg="white")
logo_label.pack(pady=20)

# Frame for inputs and button
input_frame = tk.Frame(root, bg="white")
input_frame.pack(pady=10)

# Voice button
voice_button = ttk.Button(input_frame, text="Voice", command=record_and_transcribe_faster)
voice_button.grid(row=0, column=0, padx=5)
voice_button.config(width=10)

# Entry 1 with placeholder "Name"
entry1 = ttk.Entry(input_frame, width=20, font=("Segoe UI", 12))
entry1.grid(row=0, column=1, padx=5)
entry1.insert(0, "Name")
entry1.config(foreground='gray')
entry1.bind("<FocusIn>", lambda e: on_entry_click(entry1, "Name"))
entry1.bind("<FocusOut>", lambda e: on_focusout(entry1, "Name"))

# Entry 2 with placeholder "Address"
entry2 = ttk.Entry(input_frame, width=20, font=("Segoe UI", 12))
entry2.grid(row=0, column=2, padx=5)
entry2.insert(0, "Address")
entry2.config(foreground='gray')
entry2.bind("<FocusIn>", lambda e: on_entry_click(entry2, "Address"))
entry2.bind("<FocusOut>", lambda e: on_focusout(entry2, "Address"))

# Save button
save_button = ttk.Button(input_frame, text="Save", command=save_data)
save_button.grid(row=0, column=3, padx=5)
save_button.config(width=10)

def parse_and_fill_fields(text):
    print(text)
    text = text.lower()
    name = ""
    address = ""

    if "name" in text and "address" in text:
        try:
            name_start = text.index("name") + len("name")
            address_start = text.index("address")

            name = text[name_start:address_start].strip()
            address = text[address_start + len("address"):].strip()
        except Exception as e:
            messagebox.showerror("Parsing Error", f"Could not extract fields:\n{e}")
            return

    if name:
        entry1.delete(0, "end")
        entry1.insert(0, name)
        entry1.config(foreground='black')

    if address:
        entry2.delete(0, "end")
        entry2.insert(0, address)
        entry2.config(foreground='black')

root.mainloop()
stream.stop_stream()
stream.close()
audio.terminate()