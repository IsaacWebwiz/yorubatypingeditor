import customtkinter as ctk
from tkinter import Tk, Text, END, Listbox, SINGLE, Button, font, StringVar, OptionMenu, filedialog, messagebox
import difflib
import os
import subprocess
import tempfile

def load_dictionary():
    with open('yoruba_dictionary.txt', 'r', encoding='utf-8') as file:
        dictionary = set(word.strip() for word in file)
    return dictionary

class KeyboardApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Keyboard with Auto-Correct Feature")
        self.root.geometry("1000x800")

        self.is_uppercase = False

        # Text Entry Widget
        self.text_entry = Text(self.root, height=10, width=90, wrap='word', font=("Helvetica", 16))
        self.text_entry.pack(pady=20)

        # Formatting Frame
        self.formatting_frame = ctk.CTkFrame(self.root)
        self.formatting_frame.pack(pady=5)

        # Formatting Buttons
        self.bold_button = Button(self.formatting_frame, text="Bold", command=self.toggle_bold)
        self.bold_button.pack(side='left', padx=5)

        self.italic_button = Button(self.formatting_frame, text="Italic", command=self.toggle_italic)
        self.italic_button.pack(side='left', padx=5)


        self.underline_button = Button(self.formatting_frame, text="Underline", command=self.toggle_underline)
        self.underline_button.pack(side='left', padx=5)

        # Font Options
        self.font_var = StringVar(value="Helvetica")
        self.font_menu = OptionMenu(self.formatting_frame, self.font_var, "Helvetica", "Arial", "Times New Roman", command=self.change_font)
        self.font_menu.pack(side='left', padx=5)

        # Font Size Options
        self.font_size_var = StringVar(value="16")
        self.font_size_menu = OptionMenu(self.formatting_frame, self.font_size_var, "10", "12", "14", "16", "18", "20", "22", "24", command=self.change_font_size)
        self.font_size_menu.pack(side='left', padx=5)

        # Suggestions Listbox
        self.suggestions_listbox = Listbox(self.root, selectmode=SINGLE, height=6, width=90, font=("Helvetica", 16))
        self.suggestions_listbox.pack(pady=10)
        self.suggestions_listbox.bind('<<ListboxSelect>>', self.apply_suggestion)

        # Keyboard Frame
        self.keyboard_frame = ctk.CTkFrame(self.root)
        self.keyboard_frame.pack()

        # Save, Open, and Print Buttons
        self.save_button = Button(self.root, text="Save", command=self.save_file)
        self.save_button.pack(side='left', padx=5, pady=10)

        self.open_button = Button(self.root, text="Open", command=self.open_file)
        self.open_button.pack(side='left', padx=5, pady=10)

        self.print_button = Button(self.root, text="Print", command=self.print_file)
        self.print_button.pack(side='left', padx=5, pady=10)

        # Load Dictionary
        self.dictionary = load_dictionary()

        # Keyboard Layout
        self.keys = {
            'row1': ['1', '2', '3', '4', '5', '6', '7', '8', '9', '0', '◀'],
            'row2': ['tab', 'á', 'à', 'a', 'é', 'è', 'ẹ', 'e', 'í', 'ì', 'i', 'ó', 'ò', 'ọ', 'ú', 'ù', 'u', 'ń', 'ṣ', 'ṭ', 'c', 'q', 'v'],
            'row3': ['⋀', 'á', 'à', 'a', 'é', 'è', 'ẹ', 'í', 'ì', 'i', 'ó', 'ò', 'ọ', 'o', 'ú', 'ù', 'u', 'ṅ', 'ṣ', 'ṭ', 'w', 'x', 'y'],
            'row4': ['b', 'd', 'f', 'gb', 'g', 'h', 'j', 'k', 'l', 'm', 'n', 'p', 'r', 's', 'ṣ', 'ṭ', 'z', 'Enter'],
            'row5': ['{', '}', '=', ' space ', '-', '~', "'"]
        }
        
        self.keys_uppercase = {
            'row1': ['!', '@', '#', '$', '%', '^', '&', '*', '(', ')', '◀'],
            'row2': ['Tab','Á', 'À', 'A', 'É', 'È', 'Ẹ', 'E', 'Í', 'Ì', 'I', 'Ó', 'Ò', 'Ọ', 'Ú', 'Ù', 'U', 'Ṅ', 'Ṣ', 'Ṭ', 'C', 'Q', 'V'],
            'row3': ['⋁','Á', 'À', 'A', 'É', 'È', 'Ẹ', 'Í', 'Ì', 'I', 'Ó', 'Ò', 'Ọ', 'O', 'Ú', 'Ù', 'U', 'Ṅ', 'Ṣ', 'Ṭ', 'W', 'X', 'Y'],
            'row4': ['B', 'D', 'F', 'GB', 'G', 'H', 'J', 'K', 'L', 'M', 'N', 'P', 'R', 'S', 'Ṣ', 'Ṭ', 'Z', 'Enter'],
            'row5': ['[', ']', '+', ' space ', '_', '`', '"']
        }

        # Initial Keyboard Setup
        self.create_keyboard()

    def create_keyboard(self):
        for widget in self.keyboard_frame.winfo_children():
            widget.destroy()

        keys = self.is_uppercase and self.keys_uppercase or self.keys

        for row in keys.values():
            key_row = ctk.CTkFrame(self.keyboard_frame)
            key_row.pack(side='top', pady=5)
            for key in row:
                if key == ' space ':
                    button = ctk.CTkButton(key_row, text='Space', width=60, height=40, font=("Helvetica", 16), command=lambda k=' ': self.insert_text(k))
                elif key == '◀':
                    button = ctk.CTkButton(key_row, text=key, width=60, height=40, font=("Helvetica", 16), command=self.backspace_text)
                elif key == 'Enter':
                    button = ctk.CTkButton(key_row, text=key, width=60, height=40, font=("Helvetica", 16), command=lambda k='\n': self.insert_text(k))
                elif key == '⋀' or key == '⋁':
                    button = ctk.CTkButton(key_row, text=key, width=60, height=40, font=("Helvetica", 16), command=self.toggle_case)
                else:
                    button = ctk.CTkButton(key_row, text=key, width=60, height=40, font=("Helvetica", 16), command=lambda k=key: self.insert_text(k))
                button.pack(side='left', padx=5)

    def toggle_case(self):
        self.is_uppercase = not self.is_uppercase
        self.create_keyboard()

    def insert_text(self, key):
        self.text_entry.insert(END, key)
        self.check_spelling()

    def backspace_text(self):
        current_text = self.text_entry.get("1.0", END)
        self.text_entry.delete("1.0", END)
        self.text_entry.insert("1.0", current_text[:-2])
        self.check_spelling()

    def check_spelling(self):
        self.text_entry.tag_remove("highlight", "1.0", END)
        words = self.text_entry.get("1.0", END).split()
        suggestions = []
        self.suggestions_listbox.delete(0, END)
        for word in words:
            if word and word not in self.dictionary:
                close_matches = difflib.get_close_matches(word, self.dictionary)
                if close_matches:
                    self.highlight_word(word)
                    suggestions.append((word, close_matches[0]))
                else:
                    suggestions.append((word, "No suggestion"))
        self.update_suggestions(suggestions)

    def highlight_word(self, word):
        start_idx = self.text_entry.search(word, "1.0", END)
        end_idx = f"{start_idx}+{len(word)}c"
        self.text_entry.tag_add("highlight", start_idx, end_idx)
        self.text_entry.tag_config("highlight", background="yellow", foreground="red")

    def update_suggestions(self, suggestions):
        for word, suggestion in suggestions:
            self.suggestions_listbox.insert(END, f"Suggestion for '{word}': {suggestion}")

    def apply_suggestion(self, event):
        selection = event.widget.curselection()
        if selection:
            index = selection[0]
            suggestion_text = event.widget.get(index)
            original_word, suggestion = suggestion_text.split(": ")[0].split("'")[1], suggestion_text.split(": ")[1]
            current_text = self.text_entry.get("1.0", END)
            self.text_entry.delete("1.0", END)
            new_text = current_text.replace(original_word, suggestion.strip(), 1)
            self.text_entry.insert("1.0", new_text)
            self.suggestions_listbox.delete(index)

    def save_file(self):
        file_path = filedialog.asksaveasfilename(defaultextension=".txt", filetypes=[("Text Files", "*.txt")])
        if file_path:
            with open(file_path, 'w', encoding='utf-8') as file:
                file.write(self.text_entry.get("1.0", END))
            messagebox.showinfo("Save File", "File saved successfully.")

    def open_file(self):
        file_path = filedialog.askopenfilename(filetypes=[("Text Files", "*.txt")])
        if file_path:
            with open(file_path, 'r', encoding='utf-8') as file:
                content = file.read()
                self.text_entry.delete("1.0", END)
                self.text_entry.insert("1.0", content)
            messagebox.showinfo("Open File", "File opened successfully.")

    def print_file(self):
        temp_file = tempfile.NamedTemporaryFile(delete=False, suffix=".txt", mode='w', encoding='utf-8')
        temp_file.write(self.text_entry.get("1.0", END))
        temp_file.close()
        subprocess.run(['notepad', '/p', temp_file.name])
        os.remove(temp_file.name)

    def toggle_bold(self):
        current_font = font.Font(font=self.text_entry['font'])
        if current_font.actual()['weight'] == 'normal':
            self.text_entry.configure(font=(current_font.actual()['family'], current_font.actual()['size'], 'bold'))
        else:
            self.text_entry.configure(font=(current_font.actual()['family'], current_font.actual()['size'], 'normal'))

    def toggle_italic(self):
        current_font = font.Font(font=self.text_entry['font'])
        if current_font.actual()['slant'] == 'roman':
            self.text_entry.configure(font=(current_font.actual()['family'], current_font.actual()['size'], 'italic'))
        else:
            self.text_entry.configure(font=(current_font.actual()['family'], current_font.actual()['size'], 'roman'))

    def toggle_underline(self):
        current_font = font.Font(font=self.text_entry['font'])
        if current_font.actual()['underline'] == 0:
            self.text_entry.configure(font=(current_font.actual()['family'], current_font.actual()['size'], 'underline'))
        else:
            self.text_entry.configure(font=(current_font.actual()['family'], current_font.actual()['size']))

    def change_font(self, font_name):
        current_font = font.Font(font=self.text_entry['font'])
        self.text_entry.configure(font=(font_name, current_font.actual()['size']))

    def change_font_size(self, font_size):
        current_font = font.Font(font=self.text_entry['font'])
        self.text_entry.configure(font=(current_font.actual()['family'], font_size))

if __name__ == "__main__":
    root = Tk()
    app = KeyboardApp(root)
    root.mainloop()
