import speech_recognition as sr
import tkinter as tk
from tkinter import messagebox
import sqlite3
import time

# Database setup
def create_table():
    conn = sqlite3.connect("notes.db")
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS notes (
            id INTEGER PRIMARY KEY,
            content TEXT,
            timestamp TEXT
        )
    """)
    conn.commit()
    conn.close()

create_table()

# Recognize speech function
def recognize_speech():
    recognizer = sr.Recognizer()
    with sr.Microphone() as source:
        recognizer.adjust_for_ambient_noise(source, duration=1)  # Adjust for noise
        status_label.config(text="Listening...", fg="#FF9800")
        root.update()
        try:
            audio = recognizer.listen(source)
            status_label.config(text="Processing...", fg="#FF5722")
            root.update()
            text = recognizer.recognize_google(audio)
            notes_text.insert(tk.END, text + "\n")
            status_label.config(text="Speech recognized!", fg="#4CAF50")
        except sr.UnknownValueError:
            messagebox.showerror("Error", "Could not understand the audio.")
            status_label.config(text="Try again", fg="#F44336")
        except sr.RequestError:
            messagebox.showerror("Error", "Could not request results from Google Speech Recognition service.")
            status_label.config(text="Network error", fg="#F44336")

# Save notes function with timestamp
def save_notes():
    content = notes_text.get("1.0", tk.END).strip()
    if not content:
        messagebox.showwarning("Warning", "No notes to save.")
        return
    
    timestamp = time.strftime("%Y-%m-%d %H:%M:%S")  # Get current time
    conn = sqlite3.connect("notes.db")
    cursor = conn.cursor()
    cursor.execute("INSERT INTO notes (content, timestamp) VALUES (?, ?)", (content, timestamp))
    conn.commit()
    conn.close()

    messagebox.showinfo("Success", "Notes saved successfully!")

# Clear notes function
def clear_notes():
    notes_text.delete("1.0", tk.END)
    messagebox.showinfo("Success", "Notes cleared!")

# View all notes function
def view_notes():
    conn = sqlite3.connect("notes.db")
    cursor = conn.cursor()
    cursor.execute("SELECT id, content, timestamp FROM notes")
    notes = cursor.fetchall()
    conn.close()

    if not notes:
        messagebox.showinfo("No Notes", "No notes available.")
        return

    view_window = tk.Toplevel(root)
    view_window.title("View All Notes")
    view_window.geometry("600x400")
    view_window.configure(bg="#F1F8E9")

    notes_listbox = tk.Listbox(view_window, width=80, height=15, font=("Arial", 10), bg="#F9F9F9", fg="#333", selectmode=tk.SINGLE)
    notes_listbox.pack(pady=10)

    for note in notes:
        notes_listbox.insert(tk.END, f"ID: {note[0]} - {note[1]} (Timestamp: {note[2]})")

    # Button to delete selected note
    def delete_note():
        selected_note = notes_listbox.curselection()
        if selected_note:
            note_id = notes_listbox.get(selected_note[0]).split(" ")[1]
            conn = sqlite3.connect("notes.db")
            cursor = conn.cursor()
            cursor.execute("DELETE FROM notes WHERE id = ?", (note_id,))
            conn.commit()
            conn.close()

            messagebox.showinfo("Deleted", f"Note with ID {note_id} deleted successfully!")
            view_notes()  # Refresh the notes list
        else:
            messagebox.showwarning("No Selection", "No note selected for deletion.")

    delete_button = tk.Button(view_window, text="🗑️ Delete Selected Note", command=delete_note, bg="#F44336", fg="white", font=("Arial", 12), padx=10, pady=5, relief="solid", borderwidth=2)
    delete_button.pack(pady=10)

# GUI setup
root = tk.Tk()
root.title("Speech-to-Text Notes")
root.geometry("500x450")
root.configure(bg="#F1F8E9")

# Title label
title_label = tk.Label(root, text="Speech-to-Text Notes", font=("Arial", 18, "bold"), bg="#4CAF50", fg="white")
title_label.pack(pady=20, fill="x")

# Status label
status_label = tk.Label(root, text="Click 'Start Recording' to begin", font=("Arial", 12), bg="#F1F8E9", fg="#555")
status_label.pack(pady=5)

# Record button
record_button = tk.Button(root, text="🎤 Start Recording", font=("Arial", 14), command=recognize_speech, bg="#4CAF50", fg="white", padx=20, pady=10, borderwidth=3, relief="solid")
record_button.pack(pady=10)

# Notes text box
notes_text = tk.Text(root, height=8, width=50, font=("Arial", 12), bg="#FFFFFF", fg="#333", borderwidth=3, relief="solid")
notes_text.pack(pady=5)

# Button frame
button_frame = tk.Frame(root, bg="#F1F8E9")
button_frame.pack(pady=10)

# Save button
save_button = tk.Button(button_frame, text="💾 Save Notes", font=("Arial", 12), command=save_notes, bg="#008CBA", fg="white", padx=15, pady=8, relief="solid", borderwidth=3)
save_button.pack(side=tk.LEFT, padx=20)

# Clear button
clear_button = tk.Button(button_frame, text="🗑️ Clear Notes", font=("Arial", 12), command=clear_notes, bg="#F44336", fg="white", padx=15, pady=8, relief="solid", borderwidth=3)
clear_button.pack(side=tk.LEFT, padx=20)

# View All Notes button
view_button = tk.Button(root, text="👁️ View All Notes", font=("Arial", 14), command=view_notes, bg="#FF9800", fg="white", padx=20, pady=10, relief="solid", borderwidth=3)
view_button.pack(pady=20)

root.mainloop()
