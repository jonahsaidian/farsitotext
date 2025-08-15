# %%
import threading
from tkinter import Tk, ttk
from tkinter.filedialog import askopenfilename, asksaveasfilename
from tkinter import scrolledtext

from openai import OpenAI, AuthenticationError
import os

# %%
f_transcribe = Tk()
f_transcribe.title("Farsi Transcriber")
f_transcribe.geometry("400x180")
frm = ttk.Frame(f_transcribe, padding=10, height=200, width=400)
frm.place(x=0, y=0)

# Add API key label and entry
default_api_key = os.environ.get("OPENAI_API_KEY", "")
api_label = ttk.Label(frm, text="OpenAI API Key:")
api_label.place(x=0, y=50)
api_entry = ttk.Entry(frm, width=40, show="*")
api_entry.insert(0, default_api_key)
api_entry.place(x=110, y=50)

# Add a scrolled text widget for displaying transcription (initially hidden)
transcription_box = scrolledtext.ScrolledText(frm, width=48, height=6, wrap='word')
transcription_box.place(x=0, y=120)
transcription_box.place_forget()

# Add Save and New File buttons (initially hidden)
save_btn = ttk.Button(frm, text="Save Text")
save_btn.place(x=80, y=250)
save_btn.place_forget()
new_btn = ttk.Button(frm, text="Transcribe New File")
new_btn.place(x=200, y=250)
new_btn.place_forget()

transcribed_text = ""

def on_button_press():
    fp = askopenfilename(filetypes=[('Audio Files', '*.mp3 *.mp4 *.mpeg *.mpga *.m4a *.wav *.webm')])
    if not fp:
        l1["text"] = "No file selected. Please select an audio file."
        b1["state"] = "normal"
        api_label.place(x=0, y=50)
        api_entry.place(x=110, y=50)
        return
    api_key = api_entry.get().strip()
    if not api_key:
        l1["text"] = "API key is required. Please enter your OpenAI API key."
        b1["state"] = "normal"
        api_label.place(x=0, y=50)
        api_entry.place(x=110, y=50)
        return
    valid_exts = ('.mp3', '.mp4', '.mpeg', '.mpga', '.m4a', '.wav', '.webm')
    if not fp.lower().endswith(valid_exts):
        l1["text"] = "Invalid file type. Please select a supported audio file: .mp3, .mp4, .mpeg, .mpga, .m4a, .wav, or .webm."
        b1["state"] = "normal"
        api_label.place(x=0, y=50)
        api_entry.place(x=110, y=50)
        return
    api_label.place_forget()
    api_entry.place_forget()
    transcription_box.place_forget()
    save_btn.place_forget()
    new_btn.place_forget()
    threading.Thread(target=transcribe, args=(fp,)).start()
    b1["state"] = "disabled"

def transcribe(fp):
    global transcribed_text
    l1["text"] = "Please wait as your audio file is processed."
    audio_file = open(fp, "rb")
    api_key = api_entry.get()
    try:
        client = OpenAI(api_key=api_key)
        transcription = client.audio.transcriptions.create(
            model="gpt-4o-transcribe",
            file=audio_file,
            language="fa",
            prompt="You are a farsi language expert. Please transcribe the following audio in farsi, output should be farsi text with appropriate line breaks and grammar as needed."
        )
        audio_file.close()
        transcribed_text = transcription.text
        l1["text"] = "Your audio file has been transcribed!"
        b1["state"] = "normal"
        api_label.place(x=0, y=50)
        api_entry.place(x=110, y=50)
        show_transcription_window(transcribed_text)
    except AuthenticationError:
        audio_file.close()
        l1["text"] = "Invalid API key. Please enter a valid OpenAI API key."
        b1["state"] = "normal"
        api_label.place(x=0, y=50)
        api_entry.place(x=110, y=50)
    except Exception as e:
        audio_file.close()
        l1["text"] = f"Error: {e}"
        b1["state"] = "normal"
        api_label.place(x=0, y=50)
        api_entry.place(x=110, y=50)

def show_transcription_window(text):
    win = Tk()
    win.title("Transcribed Text")
    win.geometry("600x350")
    from tkinter import scrolledtext
    text_box = scrolledtext.ScrolledText(win, width=70, height=12, wrap='word')
    text_box.pack(padx=10, pady=10)
    text_box.insert('end', text)
    text_box.config(state='disabled')

    # Disable main window while this window is open
    f_transcribe.attributes('-disabled', True)

    def reset_main_window():
        l1["text"] = "Welcome to Farsi Transcriber! \nA simple tool to transcribe Farsi (Persian) Audio to text via openai.\n"
        b1["state"] = "normal"
        api_label.place(x=0, y=50)
        api_entry.place(x=110, y=50)
        f_transcribe.attributes('-disabled', False)
        f_transcribe.lift()
        f_transcribe.focus_force()

    def on_close():
        win.destroy()
        reset_main_window()

    win.protocol("WM_DELETE_WINDOW", on_close)

    def save_text():
        save_path = asksaveasfilename(defaultextension=".txt", filetypes=[("Text files", "*.txt"), ("All files", "*.*")])
        if save_path:
            with open(save_path, "wb") as out:
                out.write(text.encode())
    def new_file():
        win.destroy()
        reset_main_window()

    btn_frame = ttk.Frame(win)
    btn_frame.pack(pady=10)
    save_btn = ttk.Button(btn_frame, text="Save Text", command=save_text)
    save_btn.pack(side='left', padx=10)
    new_btn = ttk.Button(btn_frame, text="Transcribe New File", command=new_file)
    new_btn.pack(side='left', padx=10)
    win.mainloop()

def save_text():
    return

def new_file():
    transcription_box.place_forget()
    save_btn.place_forget()
    new_btn.place_forget()
    api_label.place(x=0, y=50)
    api_entry.place(x=110, y=50)
    l1["text"] = "Welcome to Farsi Transcriber! \nA simple tool to transcribe Farsi (Persian) Audio to text via openai.\n"

save_btn.config(command=save_text)
new_btn.config(command=new_file)
# %%
l1 = ttk.Label(
    frm, text="Welcome to Farsi Transcriber! \nA simple tool to transcribe Farsi (Persian) Audio to text via openai.\n", justify="center"
)
l1.place(x=0, y=0)
b1 = ttk.Button(
    frm, text="Load File", command=on_button_press
)
b1.place(x=140, y=90)
f_transcribe.mainloop()