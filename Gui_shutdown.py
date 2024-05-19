import tkinter as tk
from tkinter import messagebox
from datetime import datetime, timedelta
import json
import os
import threading

# Class for a custom message box that automatically closes after a specified timeout.
class AutoCloseMessageBox(tk.Toplevel):
    def __init__(self, parent, title, message, timeout=60):
        """
        Initializes the custom message box.
        """
        super().__init__(parent)
        self.title(title)
        self.geometry("300x150")
        self.configure(bg="#2b2b2b")

        # Creates a label for the message.
        self.label = tk.Label(self, text=message, bg="#2b2b2b", fg="white", wraplength=280)
        self.label.pack(pady=20)
        self.timeout = timeout
        self.attributes('-topmost', True)
        
        # Updates the window's layout.
        self.update_idletasks()
        screen_width = self.winfo_screenwidth()
        screen_height = self.winfo_screenheight()
        window_width = self.winfo_width()
        window_height = self.winfo_height()
        position_right = int(screen_width / 2 - window_width / 2)
        position_down = int(screen_height / 2 - window_height / 2)
        self.geometry(f"{window_width}x{window_height}+{position_right}+{position_down}")

        # Sets up the message box to automatically close after the specified timeout.
        self.after_id = self.after(self.timeout * 1000, self.destroy)

    # Method to close the message box.
    def close(self):
        """
        Cancels the automatic closing and destroys the message box.
        """
        self.after_cancel(self.after_id)
        self.destroy()

# Class for managing scheduled shutdowns.
class ScheduleManager:
    def __init__(self, file_path):
        """
        Initializes the schedule manager with a file path.
        """
        self.file_path = file_path
        self.schedules = []
        self.load_schedules()

    # Method to load scheduled shutdowns from a file.
    def load_schedules(self):
        """
        Loads scheduled shutdowns from a file.
        """
        try:
            # Tries to open the file and load the schedules.
            with open(self.file_path, "r") as file:
                serializable_schedules = json.load(file)
                self.schedules = [datetime.fromisoformat(schedule) for schedule in serializable_schedules]
        except (FileNotFoundError, json.JSONDecodeError):
            # Handles errors when loading the file or parsing the JSON.
            self.schedules = []

    # Method to save scheduled shutdowns to a file.
    def save_schedules(self):
        """
        Saves scheduled shutdowns to a file.
        """
        try:
            # Converts the schedules to a format that can be serialized to JSON.
            serializable_schedules = [schedule.isoformat() for schedule in self.schedules]
            # Saves the schedules to the file.
            with open(self.file_path, "w") as file:
                json.dump(serializable_schedules, file)
        except Exception as e:
            # Handles any unexpected exceptions when saving the schedules.
            messagebox.showerror("Error", f"Error saving schedules: {e}")

    # Method to add a scheduled shutdown.
    def add_schedule(self, shutdown_time):
        """
        Adds a scheduled shutdown.
        """
        self.schedules.append(shutdown_time)
        self.save_schedules()

    # Method to remove a scheduled shutdown.
    def remove_schedule(self, index):
        """
        Removes a scheduled shutdown.
        """
        del self.schedules[index]
        self.save_schedules()

    # Method to remove outdated scheduled shutdowns.
    def remove_outdated_schedules(self):
        """
        Removes scheduled shutdowns that have already occurred.
        """
        now = datetime.now()
        self.schedules = [schedule for schedule in self.schedules if schedule > now]
        self.save_schedules()

# Class for the main application.
class ShutdownScheduler:
    def __init__(self, root):
        """
        Initializes the main application.
        """
        self.root = root
        self.root.title("Shutdown Scheduler")
        self.root.geometry("400x300")
        self.root.configure(bg="#2b2b2b")

        # Initializes the schedule manager.
        self.schedule_manager = ScheduleManager("shutdown_schedules.json")
        self.schedule_manager.remove_outdated_schedules()

        # Creates frames for the user interface.
        self.add_frame = tk.Frame(root, bg="#2b2b2b")
        self.schedule_frame = tk.Frame(root, bg="#2b2b2b")

        # Creates a frame for the buttons.
        self.button_frame = tk.Frame(self.root, bg="#2b2b2b")
        self.button_frame.pack(pady=20)

        # Creates buttons for adding and scheduling shutdowns.
        self.add_button = tk.Button(self.button_frame, text="Add", command=self.show_add_menu, width=20, bg="#4caf50", fg="white")
        self.schedule_button = tk.Button(self.button_frame, text="Schedule", command=self.show_schedule_menu, width=20, bg="#2196f3", fg="white")

        # Packs the buttons.
        self.add_button.pack(side="left", padx=10)
        self.schedule_button.pack(side="right", padx=10)

        # Initializes variables for the timer updates.
        self.timer_updates = []

        # Initializes flags for the 10-minute and 5-minute warnings.
        self.ten_min_warning_shown = False
        self.five_min_warning_shown = False

        # Creates a label for the timer updates.
        self.reminder_label = tk.Label(self.root, text="", width=40, bg="#2b2b2b", fg="yellow")
        self.reminder_label.pack(pady=10)

    # Method to show the menu for adding a shutdown.
    def show_add_menu(self):
        """
        Shows the menu for adding a shutdown.
        """
        # Hides the schedule frame and shows the add frame.
        self.schedule_frame.pack_forget()
        self.add_frame.pack()

        # Clears the add frame.
        for widget in self.add_frame.winfo_children():
            widget.destroy()

        # Creates labels and spinboxes for the hour and minute.
        hour_label = tk.Label(self.add_frame, text="Hour:", width=10, bg="#2b2b2b", fg="white")
        hour_label.grid(row=0, column=0, padx=10, pady=5)

        # Creates a variable for the hour and a spinbox for selecting the hour.
        self.hour_var = tk.StringVar()
        self.hour_spinbox = tk.Spinbox(self.add_frame, from_=0, to=23, width=3, font=("Arial", 14), textvariable=self.hour_var, bg="#4d4d4d", fg="white")
        self.hour_spinbox.grid(row=0, column=1, padx=10, pady=5, sticky="w")

        # Creates labels and spinboxes for the minute.
        minute_label = tk.Label(self.add_frame, text="Minute:", width=10, bg="#2b2b2b", fg="white")
        minute_label.grid(row=1, column=0, padx=10, pady=5)

        # Creates a variable for the minute and a spinbox for selecting the minute.
        self.minute_var = tk.StringVar()
        self.minute_spinbox = tk.Spinbox(self.add_frame, from_=0, to=59, width=3, font=("Arial", 14), textvariable=self.minute_var, bg="#4d4d4d", fg="white")
        self.minute_spinbox.grid(row=1, column=1, padx=10, pady=5, sticky="w")

        # Creates a button for confirming the shutdown.
        confirm_button = tk.Button(self.add_frame, text="Confirm", command=self.add_shutdown, width=20, bg="#ff5722", fg="white")
        confirm_button.grid(row=2, columnspan=2, padx=10, pady=10)

    # Method to add a shutdown.
    def add_shutdown(self):
        """
        Adds a shutdown based on the user's input.
        """
        try:
            # Gets the hour and minute from the user's input.
            hour = int(self.hour_var.get())
            minute = int(self.minute_var.get())

            # Creates a datetime object for the shutdown time.
            shutdown_time = datetime.now().replace(hour=hour, minute=minute, second=0, microsecond=0)

            # If the shutdown time is in the past, moves it to the next day.
            if shutdown_time < datetime.now():
                shutdown_time += timedelta(days=1)

            # Adds the shutdown to the schedule manager.
            self.schedule_manager.add_schedule(shutdown_time)

            # Shows a message confirming the shutdown.
            messagebox.showinfo("Success", f"Shutdown scheduled for {hour:02d}:{minute:02d}")

            # Clears the input fields.
            self.hour_var.set("")
            self.minute_var.set("")

            # Resets the warning flags.
            self.ten_min_warning_shown = False
            self.five_min_warning_shown = False

        except ValueError:
            # Handles invalid input.
            messagebox.showerror("Error", "Invalid hour or minute")

    # Method to show the menu for scheduling shutdowns.
    def show_schedule_menu(self):
        """
        Shows the menu for scheduling shutdowns.
        """
        # Hides the add frame and shows the schedule frame.
        self.add_frame.pack_forget()
        self.schedule_frame.pack()

        # Clears the schedule frame.
        for widget in self.schedule_frame.winfo_children():
            widget.destroy()

        # Gets the current time and the upcoming schedules.
        now = datetime.now()
        upcoming_schedules = [(i, schedule) for i, schedule in enumerate(self.schedule_manager.schedules) if schedule > now]

        # If there are no upcoming schedules, shows a message.
        if not upcoming_schedules:
            label = tk.Label(self.schedule_frame, text="No upcoming shutdowns", width=30, bg="#2b2b2b", fg="white")
            label.pack(pady=10)
        else:
            # For each upcoming schedule, creates a label and a button to cancel the shutdown.
            for i, (idx, schedule) in enumerate(upcoming_schedules):
                time_remaining = schedule - now
                time_remaining_str = str(time_remaining).split('.')[0]
                label = tk.Label(self.schedule_frame, text=f"Shutdown at {schedule.strftime('%H:%M')} | Time Remaining: {time_remaining_str}", width=40, bg="#2b2b2b", fg="white")
                label.grid(row=i, column=0, padx=10, pady=5)

                cancel_button = tk.Button(self.schedule_frame, text="Cancel", command=lambda idx=idx: self.cancel_shutdown(idx), width=10, bg="#ff5722", fg="white")
                cancel_button.grid(row=i, column=1, padx=10, pady=5)

                # Starts the timer updates.
                self.timer_updates.append(self.root.after(1000, lambda idx=idx, shutdown_time=schedule: self.update_timer(idx, shutdown_time)))

    # Method to update the timer.
    def update_timer(self, idx, shutdown_time):
        """
        Updates the timer for a shutdown.
        """
        now = datetime.now()
        time_remaining = shutdown_time - now

        if abs(time_remaining.total_seconds() - 600) < 1 and not self.ten_min_warning_shown:
            # Shows a 10-minute warning.
            self.show_auto_close_message("Reminder", "10 minutes remaining until shutdown", 60)
            self.ten_min_warning_shown = True
        elif abs(time_remaining.total_seconds() - 300) < 1 and not self.five_min_warning_shown:
            # Shows a 5-minute warning.
            self.show_auto_close_message("Warning", "5 minutes remaining until shutdown", 60)
            self.five_min_warning_shown = True
        elif abs(time_remaining.total_seconds() - 1) < 1:
            # Shuts down the system.
            os.system("shutdown -s -t 0")

        time_remaining_str = str(time_remaining).split('.')[0]
        slaves = self.schedule_frame.grid_slaves(row=idx, column=0)
        if slaves:
            label = slaves[0]
            label.config(text=f"Shutdown at {shutdown_time.strftime('%H:%M')} | Time Remaining: {time_remaining_str}")

        # Updates the timer.
        self.timer_updates[idx] = self.root.after(1000, lambda: self.update_timer(idx, shutdown_time))

    # Method to show an auto-close message.
    def show_auto_close_message(self, title, message, timeout):
        """
        Shows an auto-close message.
        """
        messagebox_thread = threading.Thread(target=self._show_message_in_thread, args=(title, message, timeout))
        messagebox_thread.start()

    # Method to show a message in a separate thread.
    def _show_message_in_thread(self, title, message, timeout):
        """
        Shows a message in a separate thread.
        """
        dialog = AutoCloseMessageBox(self.root, title, message, timeout)
        dialog.grab_set()
        self.root.wait_window(dialog)

    # Method to cancel a shutdown.
    def cancel_shutdown(self, index):
        """
        Cancels a shutdown.
        """
        # Cancels the timer update.
        self.root.after_cancel(self.timer_updates[index])
        # Removes the shutdown from the schedule manager.
        self.schedule_manager.remove_schedule(index)
        # Shows the schedule menu again.
        self.show_schedule_menu()

# Creates the main application.
root = tk.Tk()
app = ShutdownScheduler(root)
root.mainloop()
