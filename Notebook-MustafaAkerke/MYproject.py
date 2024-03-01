import tkinter as tk
from datetime import datetime
from tkinter import *
from tkinter import font
from tkcalendar import Calendar
import psycopg2
import threading
from plyer import notification
from tkinter import messagebox
class NBGUI:
    def __init__(self, z):
        self.z = z
        z.title('Notebook')
        z.geometry("670x500+700+10")
        z.resizable(False, False)
        self.icon = tk.PhotoImage(file='notebook.png')
        z.iconphoto(False, self.icon)
        z.config(bg='#C992E2')
        self.notes = []
        self.conn = psycopg2.connect(
            dbname="notebook",
            user="postgres",
            password="1407",
            host="localhost",
            port="5432"
        )
        self.cursor = self.conn.cursor()
        try:
            self.cursor.execute('''CREATE TABLE IF NOT EXISTS notes 
            (Title TEXT,
            Text TEXT,
            Date TEXT,
            Time TEXT);
            ''')
            self.conn.commit()
        except Exception as e:
            print("Error occurred while creating table:", e)

        self.selected_date = None
        self.selected_hour = None
        self.selected_minute = None

        delete_icon = tk.PhotoImage(file='recycle-can.png')
        self.delete_icon = delete_icon.subsample(18)

        edit_icon = tk.PhotoImage(file = 'pen.png')
        self.edit_icon = edit_icon.subsample(18)
    def createaddbutton(self):
        plus_icon = tk.PhotoImage(file='plus.png')
        self.plus_icon = plus_icon.subsample(5)
        self.btn1 = tk.Button(self.z, image=self.plus_icon, bd=0, bg='#C992E2', command=self.addNote)
        self.btn1.place(relx=0.99, rely=0.99, anchor='se')

    def addNote(self):
        newNote = Toplevel(self.z)
        newNote.title('Note')
        newNote.iconphoto(False, self.icon)
        newNote.resizable(False, False)
        newNote.geometry("540x700+30+10")
        custom_font = font.Font(family="Arial", size=12, weight="normal", slant="roman")

        self.Ntitle_label = Label(newNote, text="Title:", font=(custom_font, 20))
        self.Ntitle_label.grid(row=0, column=0, padx=5, pady=5, sticky="e")

        self.Ntitle_entry = Entry(newNote, width=50, font=custom_font, borderwidth=0.5, relief="solid")
        self.Ntitle_entry.grid(row=0, column=1, padx=5, pady=5, sticky="w")

        self.text_area = Text(newNote, width=50, height=30, font=custom_font, borderwidth=0.5, relief="solid")
        self.text_area.grid(row=5, column=0, columnspan=2, padx=5, pady=5)

        self.editFrame = Frame(newNote, bg="red", bd=5)
        self.editFrame.grid(row=2, column=0, columnspan=2, padx=5, pady=5)

        save_button = Button(newNote, text="Save", command=lambda: self.saveNote(newNote))
        save_button.grid(row=6, column=0, columnspan=2, padx=5, pady=5, sticky="ew")

    def saveNote(self, newNote):
        title = self.Ntitle_entry.get()
        text = self.text_area.get("1.0", "end-1c")
        selected_time = f"{self.selected_hour}:{self.selected_minute}"
        if not title:
            messagebox.showwarning("Warning", "Please enter a title for the note.")
            return
        try:
            self.cursor.execute('INSERT INTO notes (Title, Text, Date, Time) VALUES (%s, %s, %s, %s)',
                                (title, text, self.selected_date, selected_time))
            self.conn.commit()

            self.schedule_notification()
        except Exception as e:
            print(e)
        self.rightFrame()
        newNote.destroy()

    def validate_date(self, selected_date):
        selected_date_obj = datetime.strptime(selected_date, '%m/%d/%y').date()
        today_date = datetime.now().date()
        return selected_date_obj >= today_date
    def calendar(self):
        def save_selected_date():
            selected_date = self.calendar_widget.get_date()
            if self.validate_date(selected_date):
                self.selected_date = selected_date
                self.schedule_notification()
            else:
                messagebox.showwarning("Warning", "Please select a future date.")

        self.calendar_widget = Calendar(self.z)
        self.calendar_widget['background'] = '#abe292'
        self.calendar_widget['foreground'] = '#294059'
        self.calendar_widget['selectbackground'] = '#abe292'
        self.calendar_widget['headersbackground'] = '#CCCCCC'
        self.calendar_widget['weekendbackground'] = '#CCCCCC'
        calendar_font = font.Font(family="Roboto", size=11, weight="normal", slant="roman")
        self.calendar_widget.config(font=calendar_font)
        self.calendar_widget.place(x=20, y=15, width=300, height=300)

        self.select_date_button.config(command=save_selected_date)


    def time(self):
        def save_selected_time():
            self.selected_hour = self.hour_var.get()
            self.selected_minute = self.minute_var.get()

        time_picker_frame = Frame(self.z, bg='#F1E9EF')
        time_picker_frame.place(x=20, y=370)

        hour_label = Label(time_picker_frame, text="Hour:", bg='#F1E9EF', fg='#294059', font=('Arial', 12))
        hour_label.grid(row=0, column=0, padx=10, pady=1)
        self.hour_var = StringVar()
        validate_hour = self.z.register(self.validate_hour)
        self.hour_spinbox = Spinbox(time_picker_frame, from_=0, to=23, textvariable=self.hour_var, width=5,
                                    font=('Arial', 12), validate="key", validatecommand=(validate_hour, "%P"))
        self.hour_spinbox.grid(row=0, column=1, padx=1, pady=5)

        minute_label = Label(time_picker_frame, text="Minute:", bg='#F1E9EF', fg='#294059', font=('Arial', 12))
        minute_label.grid(row=0, column=2, padx=25, pady=10)
        self.minute_var = StringVar()
        validate_minute = self.z.register(self.validate_minute)
        self.minute_spinbox = Spinbox(time_picker_frame, from_=0, to=59, textvariable=self.minute_var, width=5,
                                      font=('Arial', 12), validate="key", validatecommand=(validate_minute, "%P"))
        self.minute_spinbox.grid(row=0, column=3, padx=2, pady=5)

        self.select_time_button.config(command=save_selected_time)

    def validate_hour(self, value):
        if value.isdigit():
            num_value = int(value)
            return 0 <= num_value <= 23
        return False

    def validate_minute(self, value):
        if value.isdigit():
            num_value = int(value)
            return 0 <= num_value <= 59
        return False

    def select_date_button(self):
        self.select_date_button = tk.Button(self.z, text='Select Date', command=self.calendar)
        self.select_date_button.config(bg='#abe292', width=25, font=('Arial', 12))
        self.select_date_button.place(relx=0.25, rely=0.69, anchor=CENTER)

    def select_time_button(self):
        self.select_time_button = tk.Button(self.z, text='Select Time', command=self.time)
        self.select_time_button.config(bg='#abe292', width=25, font=('Arial', 12))
        self.select_time_button.place(relx=0.25, rely=0.90, anchor=CENTER)

    def rightFrame(self):
        self.rframe = Frame(self.z, bg="#C992E2")
        self.rframe.place(width=330, height=380, relx=1, x=-15, y=10, anchor='ne')

        scrollbar = Scrollbar(self.rframe, orient=VERTICAL)
        scrollbar.pack(side=RIGHT, fill=Y)

        canvas = Canvas(self.rframe, bg="#C992E2", yscrollcommand=scrollbar.set)
        canvas.pack(side=LEFT, fill=BOTH, expand=True)
        scrollbar.config(command=canvas.yview)

        inner_frame = Frame(canvas, bg="#C992E2")
        canvas.create_window((0, 0), window=inner_frame, anchor='nw')
        try:
            self.cursor.execute("SELECT Title FROM notes")
            notes = self.cursor.fetchall()
            for note in notes:
                frame = Frame(inner_frame, bg="#FFFFFF", bd=1, relief="solid")
                frame.pack(fill="x", padx=5, pady=5)

                title_label = Label(frame, text=note[0], bg="#FFFFFF", fg="#294059", font=("Arial", 12), wraplength=250)
                title_label.pack(side="left", padx=5, pady=5)

                edit_button = Button(frame, image = self.edit_icon, command=lambda note_title=note[0]: self.openNote(note_title))
                edit_button.image = self.edit_icon
                edit_button.pack(side="right", padx=5, pady=5)

                delete_button = Button(frame, image=self.delete_icon,
                                       command=lambda note_title=note[0]: self.deleteNote(note_title))
                delete_button.image = self.delete_icon
                delete_button.pack(side="right", padx=5, pady=5)

        except Exception as e:
            print("Error occurred while adding note frames:", e)

        self.rframe.update_idletasks()
        canvas.config(scrollregion=canvas.bbox("all"))

    def deleteNote(self, note_title):
        confirm = messagebox.askyesno("Delete", "Are you sure you want to delete this note?")
        if confirm:
            try:
                self.cursor.execute('DELETE FROM notes WHERE Title = %s', (note_title,))
                self.conn.commit()
                print("Note deleted successfully.")
                self.rightFrame()
            except Exception as e:
                print("Error occurred while deleting note:", e)

    def openNote(self, note_title):
        try:
            self.cursor.execute("SELECT * FROM notes WHERE Title = %s", (note_title,))
            note = self.cursor.fetchone()
            if note:
                edit_window = Toplevel(self.z)
                edit_window.title("Edit Note")
                edit_window.iconphoto(False, self.icon)
                edit_window.resizable(False, False)
                edit_window.geometry("540x700+30+10")
                custom_font = font.Font(family="Arial", size=12, weight="normal", slant="roman")

                title_label = Label(edit_window, text="Title:", font=(custom_font, 20))
                title_label.grid(row=0, column=0, padx=5, pady=5, sticky="e")

                title_entry = Entry(edit_window, width=50, font=custom_font, borderwidth=0.5, relief="solid")
                title_entry.insert(END, note[0])
                title_entry.grid(row=0, column=1, padx=5, pady=5, sticky="w")

                text_area = Text(edit_window, width=50, height=30, font=custom_font, borderwidth=0.5, relief="solid")
                text_area.insert(END, note[1])
                text_area.grid(row=1, column=0, columnspan=2, padx=5, pady=5)

                save_button = Button(edit_window, text="Save",
                                     command=lambda: self.saveEditedNote(edit_window, title_entry.get(),
                                                                         text_area.get("1.0", "end-1c"), note[0]))
                save_button.grid(row=2, column=0, columnspan=2, padx=5, pady=5, sticky="ew")
        except Exception as e:
            print("Error occurred while opening note for editing:", e)

    def saveEditedNote(self, edit_window, new_title, text, old_title):
        try:
            self.cursor.execute("UPDATE notes SET Title = %s, Text = %s WHERE Title = %s", (new_title, text, old_title))
            self.conn.commit()
            print("Note edited successfully.")
            self.rightFrame()
        except Exception as e:
            print("Error occurred while saving edited note:", e)
        edit_window.destroy()

    def save_selected_date(self):
        self.selected_date = self.calendar_widget.get_date()
        self.schedule_notification()

    def save_selected_time(self):
        self.selected_hour = self.hour_var.get()
        self.selected_minute = self.minute_var.get()
        self.schedule_notification()

    def schedule_notification(self):
        if self.selected_date and self.selected_hour and self.selected_minute:
            date_obj = datetime.strptime(self.selected_date, '%m/%d/%y').date()
            time_str = f"{self.selected_hour}:{self.selected_minute}"
            time_obj = datetime.strptime(time_str, '%H:%M').time()
            note_title = self.Ntitle_entry.get()
            self.send_notification_at(date_obj, time_obj, note_title)

    def send_notification_at(self, date_obj, time_obj, note_title):
        notification_datetime = datetime.combine(date_obj, time_obj)
        time_difference = notification_datetime - datetime.now()
        notification_delay_seconds = time_difference.total_seconds()
        threading.Timer(notification_delay_seconds, lambda: notification.notify(
            title='Notebook',
            message=f' {note_title}',
        )).start()


if __name__ == "__main__":
    z = tk.Tk()
    notebook_gui = NBGUI(z)
    notebook_gui.createaddbutton()
    notebook_gui.select_date_button()
    notebook_gui.select_time_button()
    notebook_gui.rightFrame()
    z.mainloop()
