import os
import customtkinter as ctk
import sqlite3
from PIL import Image, ImageTk

# database connection
connection = sqlite3.connect('airhockey.db')
c = connection.cursor()

# function to fetch data from the database and update the widget
def update_widget():
    c.execute('SELECT * FROM scoreset LIMIT 7')
    rows = c.fetchall()
    animated_panel.delete_all_widgets()  # Clear existing labels
    ctk.CTkLabel(animated_panel, text="Name"+"\t\t\t"+"Score"+"\t"+"Time").pack(padx=4, pady=4)
    for row in rows:
        ctk.CTkLabel(animated_panel, text=row[0]+"\t\t\t   "+str(row[1])+"\t"+str(row[2])).pack(expand=True, fill='both', padx=4, pady=4)
    ctk.CTkTextbox(animated_panel, fg_color=('#dbdbdb', '#2b2b2b')).pack(expand=True, fill='both', pady=10)
    animated_panel.after(40000, update_widget)

# send player names to Game
def get_text_value():
    value1 = name_entry1.get()
    value2 = name_entry2.get()
    print("Player1: ", value1)
    print("Player2: ", value2)
    os.environ["P1"] = value1
    os.environ["P2"] = value2

def runGame():
    window.withdraw()
    os.system('python airhockey.py')
    window.deiconify()

def combined_command():
    get_text_value()
    runGame()

class SlidePanel(ctk.CTkFrame):
    def __init__(self, parent, start_pos, end_pos):
        super().__init__(master=parent)

        # general attributes
        self.start_pos = start_pos + 0.02
        self.end_pos = end_pos - 0.02
        self.width = abs(start_pos - end_pos)
        self.height = 0.8

        # animation logic
        self.pos = self.start_pos
        self.in_start_pos = True

        # layout
        self.place(relx=self.start_pos, rely=(1 - self.height) / 2, relwidth=self.width, relheight=self.height)

    def animate(self):
        if self.in_start_pos:
            self.animate_forward()
        else:
            self.animate_backwards()

    def animate_forward(self):
        if self.pos > self.end_pos:
            self.pos -= 0.008
            self.place(relx=self.pos, rely=(1 - self.height) / 2, relwidth=self.width, relheight=self.height)
            self.after(10, self.animate_forward)
        else:
            self.in_start_pos = False

    def animate_backwards(self):
        if self.pos < self.start_pos:
            self.pos += 0.008
            self.place(relx=self.pos, rely=(1 - self.height) / 2, relwidth=self.width, relheight=self.height)
            self.after(10, self.animate_backwards)
        else:
            self.in_start_pos = True

    def delete_all_widgets(self):
        for child in self.winfo_children():
            child.destroy()

# window
window = ctk.CTk()
window.title('Air Hockey ')
window.geometry('800x400')

# Load and display the image
image_path = 'gamelogo.png'  # Replace with the actual path to your image file
image = Image.open(image_path)
image = image.resize((370, 370))  # Adjust the size as needed
image_tk = ImageTk.PhotoImage(image)

image_label = ctk.CTkLabel(window, image=image_tk, text='')
image_label.place(relx=0.4, rely=0.5, anchor='center')

# animated widget
animated_panel = SlidePanel(window, 1.0, 0.6)
ctk.CTkLabel(animated_panel, text="Name"+"\t\t\t"+"Score"+"\t"+"Time").pack(padx=4, pady=4)  # Reduce vertical padding
# Start fetching and updating the widget
update_widget()

# Text box for entering name
name_entry1 = ctk.CTkEntry(window, width=140)
name_entry1.insert(0, '       Enter Name P1')
name_entry1.place(relx=0.1, rely=0.38, anchor='center')

name_entry2 = ctk.CTkEntry(window, width=140)
name_entry2.insert(0, '       Enter Name P2')
name_entry2.place(relx=0.1, rely=0.46, anchor='center')

def on_entry_typing(event):
    if name_entry1.get() == '       Enter Name P1':
        name_entry1.delete(0, 'end')
    if name_entry2.get() == '       Enter Name P2':
        name_entry2.delete(0, 'end')

name_entry1.bind('<Key>', on_entry_typing)
name_entry2.bind('<Key>', on_entry_typing)

# button
button = ctk.CTkButton(window, text='View Scores', command=animated_panel.animate)
button.place(relx=0.1, rely=0.54, anchor='center')

buttonStart = ctk.CTkButton(window, text='Start Game', command=combined_command)
buttonStart.place(relx=0.1, rely=0.62, anchor='center')

# run
window.mainloop()
