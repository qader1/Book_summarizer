from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_community.document_loaders import PyPDFLoader
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from PIL import Image, ImageTk
import shutil
import pypandoc
import threading
import sys
import json
import os


try:
    BASE_PATH = sys._MEIPASS
except Exception:
    BASE_PATH = os.path.abspath(".")


def summarize(stop_event, callback):
    with open(os.path.join(BASE_PATH, "key.json")) as f:
        os.environ["GOOGLE_API_KEY"] = json.load(f)["key"]

    llm = ChatGoogleGenerativeAI(
        model="gemini-1.5-flash",
        temperature=0,
        max_tokens=None,
        timeout=None,
        max_retries=2
    )

    try:
        pdf = PyPDFLoader(name_src_value.get())
        pages = [doc.page_content for doc in pdf.load()]
        if slice_var.get():
            pages = pages[int(spinbox1_var.get())-1: int(spinbox2_var.get())]
        strings = "\n".join(pages).encode("utf-8")
    except IndexError as e:
        messagebox.showerror("An Error Occurred",
                             f"Upper slice value seems to exceed the number of pages\n{e}")
        callback(False)
        return
    except Exception as e:
        messagebox.showerror("An Error Occurred",
                             f"An error occurred while parsing the PDF\n{e}")
        callback(False)
        return

    messages = [
        (
            "system",
            "Your task is summarize books. If the document provided is long and constitutes multiple chapters, "
            "you summarize the chapters while taking context into account. Summaries should be long. "
            "If it's a short document, you could summarize it directly."
            "You should also create notes whenever is needed to highlight important "
            "information or contexts in each chapter's summary. Users are students and they need your help to get "
            "good grades and be successful. Summary should be in markdown",
        ),
        ("human", f"Book/Document content:\n{strings}"),
    ]
    try:
        ai_message = llm.invoke(messages)
        content = ai_message.content
        destination = os.path.join(
            name_dest_value.get(),
            "SUMMARY_" + os.path.basename(name_src_value.get()) + ".docx"
        )
        if not stop_event.is_set():
            pandoc_path = shutil.which("pandoc")
            if pandoc_path is None:
                pypandoc.download_pandoc()
            pypandoc.convert_text(content, "docx", format="md", outputfile=destination, encoding="utf-8")
            callback(True)
    except Exception as e:
        messagebox.showerror("An Error Occurred", f"An error occurred while connecting to google's cloud\n{e}")
        callback(False)

def show_loading_dialog():
    dialog = tk.Toplevel(root)
    dialog.title("Loading..")
    dialog.geometry("300x50")
    dialog.geometry("+300+300")

    label = ttk.Label(dialog, text="Please wait while getting the summary from the AI..")
    label.pack()
    progress_bar = ttk.Progressbar(dialog, mode='indeterminate', length=260)
    progress_bar.pack()
    progress_bar.start()

    stop_event = threading.Event()

    def close_dialog(success=False):
        progress_bar.stop()
        dialog.destroy()
        if success and not stop_event.is_set():
            tk.messagebox.showinfo("Done", "The document was summarized successfully!")

    def on_closing():
        stop_event.set()
        dialog.destroy()

    dialog.protocol("WM_DELETE_WINDOW", on_closing)

    thread = threading.Thread(target=summarize, args=(stop_event, close_dialog))
    thread.start()

    dialog.transient(root)
    dialog.grab_set()
    root.wait_window(dialog)


def open_file():
    filepath = filedialog.askopenfilename(
        filetypes=[("PDF file", "*.pdf"), ("All files", "*.*")]
    )

    if not filepath:
        return

    name_src_value.set(filepath)
    destination_button.config(state=tk.NORMAL)


def select_dir():
    filepath = filedialog.askdirectory(
        initialdir=os.path.dirname(name_src_value.get())
    )
    if not filepath:
        return
    name_dest_value.set(filepath)
    summarize_button.config(state=tk.NORMAL)

def open_image_dialog():
    dialog = tk.Toplevel(root)
    dialog.title("With love")
    dialog.geometry("305x305")
    dialog.resizable(False, False)

    image_path = os.path.join(BASE_PATH, "mai_qdr.jpg")
    image = Image.open(image_path)
    photo = ImageTk.PhotoImage(image)

    label = ttk.Label(dialog, image=photo)
    label.image = photo
    label.pack()

    dialog.transient(root)
    dialog.grab_set()
    root.wait_window(dialog)

def validate_spinbox1(*args):
    value1 = int(spinbox1_var.get())
    value2 = int(spinbox2_var.get())
    if value1 > value2:
        spinbox2_var.set(str(value1))

def validate_spinbox2(*args):
    value1 = int(spinbox1_var.get())
    value2 = int(spinbox2_var.get())
    if value1 > value2:
        spinbox1_var.set(str(value2))


def toggle_spinboxes():
    if slice_var.get():
        spinbox1.grid(row=2, column=2, padx=5, pady=5, sticky=tk.W)
        spinbox2.grid(row=2, column=2, padx=5, pady=5, sticky=tk.E)
    else:
        spinbox1.grid_remove()
        spinbox2.grid_remove()


# Create the main window
root = tk.Tk()
root.title("PDF Summarizer")
root.resizable(width=False, height=False)

file_src_label = ttk.Label(root, text="Source:")
file_src_label.grid(row=0, column=0, padx=5, pady=5)

name_src_value = tk.StringVar()
file_src = ttk.Entry(root, width=60, textvariable=name_src_value)
file_src.config(state='disabled')
file_src.grid(row=0, column=1)

file_dest_name_label = ttk.Label(root, text="Destination:")
file_dest_name_label.grid(row=1, column=0, padx=5, pady=5)

name_dest_value = tk.StringVar()
file_dest_name = ttk.Entry(root, width=60, textvariable=name_dest_value)
file_dest_name.config(state='disabled')
file_dest_name.grid(row=1, column=1)

source_button = ttk.Button(root, text="Select Source", width=20, command=open_file)
source_button.grid(row=0, column=2, padx=5, pady=5)

destination_button = ttk.Button(root, text="Select Destination", width=20, command=select_dir)
destination_button.grid(row=1, column=2, padx=5, pady=5)
destination_button.config(state='disabled')

slice_lbl = ttk.Label(root, text="Slice:")
slice_lbl.grid(row=2, column=0, padx=5, pady=5)

slice_var = tk.BooleanVar(value=False)
slice_check = ttk.Checkbutton(root, variable=slice_var, command=toggle_spinboxes)
slice_check.grid(row=2, column=1, padx=5, pady=5, sticky=tk.W)

spinbox1_var = tk.StringVar(value="1")
spinbox2_var = tk.StringVar(value="1")

spinbox1 = ttk.Spinbox(root,from_=1, to=1000, textvariable=spinbox1_var, width=5)
spinbox2 = ttk.Spinbox(root, from_=1, to=1000, textvariable=spinbox2_var, width=5)

spinbox1_var.trace_add("write", validate_spinbox1)
spinbox2_var.trace_add("write", validate_spinbox2)

spinbox1.grid_remove()
spinbox2.grid_remove()

summarize_button = ttk.Button(root, text="Summarize", width=20, command=show_loading_dialog)
summarize_button.grid(row=3, column=0, columnspan=2, padx=5, pady=5)
summarize_button.config(state='disabled')

abt_button = ttk.Button(root, text="About", width=20, command=open_image_dialog)
abt_button.grid(row=3, column=2, columnspan=2, padx=5, pady=5)

root.mainloop()