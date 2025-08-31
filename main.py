import re
import tkinter as tk
from tkinter import ttk, messagebox
import wave
from PIL import Image, ImageTk
import pyodbc
import pypyodbc
import os
import pyaudio
from src.transcribe import transcribe_gujarati_audio
import threading

# Define the path to your Access DB
db_path = os.path.abspath("contacts.mdb")
audio_file_path = os.path.abspath("temp_voice.wav")
conn_str = f"Driver={{Microsoft Access Driver (*.mdb, *.accdb)}};DBQ={db_path};"


def record_and_transcribe(field_type):
    fs = 44100  # sample rate
    buffer = 1024
    """
    Handles the recording process, displaying a modal window, and
    calling the transcription function after the recording is stopped.
    """
    # Create a new PyAudio instance and stream for this recording session
    audio = pyaudio.PyAudio()
    stream = audio.open(
        format=pyaudio.paInt16,
        channels=1,
        rate=fs,
        input=True,
        frames_per_buffer=buffer,
    )
    frames = []

    is_recording = True

    def record_loop():
        """Captures audio data from the stream and appends it to frames."""
        nonlocal is_recording
        try:
            while is_recording:
                data = stream.read(buffer)
                frames.append(data)
        except Exception as e:
            print("Recording error:", e)

    def stop_recording():
        """Stops the recording, saves the audio to a file, and starts processing."""
        nonlocal is_recording
        is_recording = False

        # Stop and terminate the stream properly
        stream.stop_stream()
        stream.close()
        audio.terminate()

        # Save the recorded audio to a WAV file
        try:
            sound_file = wave.open(audio_file_path, "wb")
            sound_file.setnchannels(1)
            sound_file.setsampwidth(pyaudio.PyAudio().get_sample_size(pyaudio.paInt16))
            sound_file.setframerate(fs)
            sound_file.writeframes(b"".join(frames))
            sound_file.close()

            recording_modal.destroy()
            process_audio(field_type)
        except Exception as e:
            messagebox.showerror("વૉઇસ ભૂલ", f"ઑડિયો ફાઇલ સાચવવામાં નિષ્ફળ: {e}")

    def process_audio(field_type):
        """Shows a processing modal and calls the transcription function."""
        processing_modal = tk.Toplevel(root)
        processing_modal.title("પ્રોસેસીંગ")
        processing_modal.geometry("300x100")
        processing_modal.configure(bg="white")
        processing_modal.grab_set()

        label = tk.Label(
            processing_modal,
            text="તમારા ભાષણ પર પ્રક્રિયા કરી રહ્યા છીએ...",
            bg="white",
            font=("Segoe UI", 12),
        )
        label.pack(pady=30)
        root.update()

        try:
            # Assuming transcribe_gujarati_audio and parse_and_fill_fields are defined elsewhere
            text = transcribe_gujarati_audio(audio_file_path)
            if text:
                parse_and_fill_fields(text, field_type)
            else:
                messagebox.showerror(
                    "વૉઇસ ભૂલ", "અવાજ પર પ્રક્રિયા કરવામાં નિષ્ફળ: ટ્રાન્સક્રિપ્શન અસફળ"
                )
        except Exception as e:
            messagebox.showerror("વૉઇસ ભૂલ", f"અવાજ પર પ્રક્રિયા કરવામાં નિષ્ફળ:\n{e}")
        finally:
            processing_modal.destroy()

    # Show recording modal
    recording_modal = tk.Toplevel(root)
    recording_modal.title("રેકોર્ડિંગ")
    recording_modal.geometry("300x150")
    recording_modal.configure(bg="white")
    recording_modal.grab_set()

    label = tk.Label(
        recording_modal,
        text="રેકોર્ડિંગ હમણાં ચાલુ છે\nબંધ કરવા માટે ઓકે દબાવો",
        bg="white",
        font=("Segoe UI", 12),
    )
    label.pack(pady=20)

    ok_button = ttk.Button(recording_modal, text="ઓક", command=stop_recording)
    ok_button.pack()

    # Start recording in background thread
    stream.start_stream()
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

    if val1 == "" or val1 == "નામ" or val2 == "" or val2 == "સરનામું":
        messagebox.showwarning("માન્યતા ભૂલ", "નામ અને સરનામું બંને જરૂરી છે.")
    else:
        try:
            conn = pyodbc.connect(conn_str)
            cursor = conn.cursor()

            # Try to create the table; ignore error if it already exists
            try:
                cursor.execute(
                    """
                    CREATE TABLE contacts (
                        ID AUTOINCREMENT PRIMARY KEY,
                        Name TEXT(100),
                        Address TEXT(255)
                    )
                """
                )
            except Exception as e:
                if "already exists" in str(e):
                    pass  # Table already exists, no problem
                else:
                    raise  # Unexpected error, re-raise
            cursor.execute(
                "INSERT INTO contacts (Name, Address) VALUES (?, ?)", (val1, val2)
            )
            conn.commit()

            cursor.close()
            conn.close()

            print(f"Saved: {val1}, {val2}")
            messagebox.showinfo("સફળતા", "ડેટા સફળતાપૂર્વક સાચવ્યો!")
            entry1.delete(0, "end")
            entry1.insert(0, "નામ")
            entry1.config(foreground="gray")

            entry2.delete(0, "end")
            entry2.insert(0, "સરનામું")
            entry2.config(foreground="gray")
        except Exception as e:
            messagebox.showerror("ડેટાબેઝ ભૂલ", f"ડેટા સાચવવામાં નિષ્ફળ થયાં:\n{e}")


def on_entry_click(entry, placeholder):
    if entry.get() == placeholder:
        entry.delete(0, "end")
        entry.config(foreground="black")


def on_focusout(entry, placeholder):
    if entry.get() == "":
        entry.insert(0, placeholder)
        entry.config(foreground="gray")


# Create main window
root = tk.Tk()
root.title("HY Infotech - Voice Input")
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

# Voice button for Name
voice_button_name = ttk.Button(
    input_frame, text="નામ બોલો", command=lambda: record_and_transcribe("name")
)
voice_button_name.grid(row=0, column=0, padx=5)
voice_button_name.config(width=10)

# Entry 1 with placeholder "Name"
entry1 = ttk.Entry(input_frame, width=20, font=("Segoe UI", 12))
entry1.grid(row=0, column=1, padx=5)
entry1.insert(0, "નામ")
entry1.config(foreground="gray")
entry1.bind("<FocusIn>", lambda e: on_entry_click(entry1, "નામ"))
entry1.bind("<FocusOut>", lambda e: on_focusout(entry1, "નામ"))

# Voice button for Address
voice_button_address = ttk.Button(
    input_frame, text="સરનામું બોલો", command=lambda: record_and_transcribe("address")
)
voice_button_address.grid(row=1, column=0, padx=5, pady=5)
voice_button_address.config(width=10)

# Entry 2 with placeholder "Address"
entry2 = ttk.Entry(input_frame, width=20, font=("Segoe UI", 12))
entry2.grid(row=1, column=1, padx=5, pady=5)
entry2.insert(0, "સરનામું")
entry2.config(foreground="gray")
entry2.bind("<FocusIn>", lambda e: on_entry_click(entry2, "સરનામું"))
entry2.bind("<FocusOut>", lambda e: on_focusout(entry2, "સરનામું"))

# Save button
save_button = ttk.Button(input_frame, text="સાચવો", command=save_data)
save_button.grid(row=2, column=1, padx=5, pady=10)
save_button.config(width=10)


def parse_and_fill_fields(text, field_type):
    print("translation:", text)
    text = text.lower().strip()

    if field_type == "name":
        entry1.delete(0, "end")
        entry1.insert(0, text)
        entry1.config(foreground="black")
    elif field_type == "address":
        entry2.delete(0, "end")
        entry2.insert(0, text)
        entry2.config(foreground="black")


root.mainloop()
stream.stop_stream()
stream.close()
audio.terminate()
