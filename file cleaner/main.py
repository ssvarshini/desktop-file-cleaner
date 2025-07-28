import os
import shutil
from datetime import datetime
import json 
import tkinter as tk
from tkinter import filedialog, messagebox


path = "~/Desktop/TestOrganiser"
full_path = os.path.expanduser(path)
testOrganiser = full_path

list_of_folder = os.listdir(testOrganiser)

undo_log = []


categories = {
    "Documents": [".pdf", ".txt", ".docx"],
    "Images": [".jpg", ".png", ".gif"],
    "Audio": [".mp3", ".wav"],
    "Videos": [".mp4", ".avi", ".mov"],
    "Archives": [".zip", ".rar"]
}

def get_unique_filename(folder_path, filename):
    base_name, extension = os.path.splitext(filename)
    candidate = filename
    counter = 1

    while os.path.exists(os.path.join(folder_path, candidate)):
        candidate = f"{base_name}({counter}){extension}"
        counter += 1

    return candidate

def log_action(original_path, destination_path):
    log_name_file = "log.txt"
    log_file = os.path.join(testOrganiser, log_name_file)
    current_datetime = datetime.now()
    timestamp = current_datetime.strftime("%Y-%m-%d %H:%M:%S")

    with open(log_file, 'a') as file:
        file.write(f"{original_path} => {destination_path} @ {timestamp}\n")

def undo():
    undo_log_file = os.path.join(testOrganiser, "undo_log.json")

    if not os.path.exists(undo_log_file):
        print("No undo log found.")
        return

    with open(undo_log_file, 'r') as jsonfile:
        undo_log = json.load(jsonfile)

    for move in undo_log:
        from_path = move["from"]
        to_path = move["to"]

        if os.path.exists(to_path):
            os.makedirs(os.path.dirname(from_path), exist_ok=True)
            shutil.move(to_path, from_path)
            print(f"Moved back: {to_path} → {from_path}")
        else:
            print(f"File missing, couldn't undo: {to_path}")

    os.remove(undo_log_file)
    print("Undo completed and log removed.")

def organise_file(folder_path): 
    for item in os.listdir(folder_path):
            check_for_file = os.path.join(folder_path, item)
            if(os.path.isfile(check_for_file)):
                print(f"{check_for_file} is a file")
                parts_of_file = item.split('.')
                prefix = "." + parts_of_file[-1].lower()

                category = "Others" 

                for key in categories:
                    if prefix in categories[key]:
                        category = key
                        break

                destination_folder = os.path.join(folder_path, category)

                if not os.path.exists(destination_folder):
                    os.mkdir(destination_folder)
                    print(f"Folder {destination_folder} created successfully")

                final_filename = get_unique_filename(destination_folder, item)
                destination_path = os.path.join(destination_folder, final_filename)
                
                shutil.move(check_for_file, destination_path)
                print(f"Moved {item} to {destination_folder}")
                log_action(check_for_file, destination_path)
                undo_log.append({
                    "from": check_for_file, 
                    "to": destination_path  
                })


            else:
                print(f"{check_for_file} is not a file")



def folder_indiside_folder():
    for current_folder, _, _ in os.walk(testOrganiser):
        if current_folder == testOrganiser:  
            continue
        organise_file(current_folder)

def delete_empty():
    for item in os.listdir(testOrganiser):
        folder_path = os.path.join(testOrganiser, item)
        if os.path.isdir(folder_path) and not os.listdir(folder_path):
            os.rmdir(folder_path)

undo_log_path = os.path.join(testOrganiser, "undo_log.json")

def open_window():
    window = tk.Tk()
    window.title("File Organiser")
    window.geometry("400x200")

    label = tk.Label(window, text="Browse a folder", font=("Arial", 12))
    label.pack(pady=20)

    def browse_folder():
        folder_selected = filedialog.askdirectory()
        if folder_selected:
            global undo_log
            undo_log = []  

            organise_file(folder_selected)
            for current_folder, _, _ in os.walk(folder_selected):
                if current_folder != folder_selected:
                    organise_file(current_folder)

            undo_log_path = os.path.join(folder_selected, "undo_log.json")
            with open(undo_log_path, 'w') as jsonfile:
                json.dump(undo_log, jsonfile, indent=2)

            for item in os.listdir(folder_selected):
                folder_path = os.path.join(folder_selected, item)
                if os.path.isdir(folder_path) and not os.listdir(folder_path):
                    os.rmdir(folder_path)

            messagebox.showinfo("Success", "Files organised successfully!")

    browse_button = tk.Button(window, text="Browse Folder", command=browse_folder)
    browse_button.pack(pady=10)

    window.mainloop()

open_window()

