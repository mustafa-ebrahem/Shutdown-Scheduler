import tkinter as tk
from tkinter import messagebox
from datetime import datetime, timedelta
import json
import os
import threading

class AutoCloseMessageBox(tk.Toplevel):
    def __init__(self, parent, title, message, timeout=60):
        super().__init__(parent)
        self.title(title)
        self.geometry("300x150")
        self.configure(bg="#2b2b2b")
        self.label = tk.Label(self, text=message, bg="#2b2b2b", fg="white", wraplength=280)
        self.label.pack(pady=20)
        self.timeout = timeout
        self.attributes('-topmost', True)
        
        # Center the window on the screen
        self.update_idletasks()
        screen_width = self.winfo_screenwidth()
        screen_height = self.winfo_screenheight()
        window_width = self.winfo_width()
        window_height = self.winfo_height()
        position_right = int(screen_width / 2 - window_width / 2)
        position_down = int(screen_height / 2 - window_height / 2)
        self.geometry(f"{window_width}x{window_height}+{position_right}+{position_down}")

        self.after_id = self.after(self.timeout * 1000, self.destroy)

    def close(self):
        self.after_cancel(self.after_id)
        self.destroy()

class ShutdownScheduler:
    def __init__(self, root):
        self.root = root
        self.root.title("Shutdown Scheduler")
        self.root.geometry("400x300")
        self.root.configure(bg="#2b2b2b")
        
        self.add_frame = tk.Frame(root, bg="#2b2b2b")
        self.schedule_frame = tk.Frame(root, bg="#2b2b2b")
        
        self.add_button = tk.Button(self.root, text="Add", command=self.show_add_menu, width=20, bg="#4caf50", fg="white")
        self.schedule_button = tk.Button(self.root, text="Schedule", command=self.show_schedule_menu, width=20, bg="#2196f3", fg="white")
        
        self.add_button.pack(pady=10)
        self.schedule_button.pack(pady=10)
        
        self.shutdown_schedules = []
        self.timer_updates = []

        self.ten_min_warning_shown = False
        self.five_min_warning_shown = False
        
        self.load_schedules()  # Load schedules from file when app starts
        self.remove_outdated_schedules()

        # Create a label to show reminders
        self.reminder_label = tk.Label(self.root, text="", width=40, bg="#2b2b2b", fg="yellow")
        self.reminder_label.pack(pady=10)

    def load_schedules(self):
        try:
            with open("shutdown_schedules.json", "r") as file:
                serializable_schedules = json.load(file)
                self.shutdown_schedules = [datetime.fromisoformat(schedule) for schedule in serializable_schedules]
        except FileNotFoundError:
            pass
        except json.JSONDecodeError:
            pass
        
    def remove_outdated_schedules(self):
        now = datetime.now()
        outdated_indexes = []
        for i, schedule in enumerate(self.shutdown_schedules):
            if schedule <= now:
                outdated_indexes.append(i)
        for idx in reversed(outdated_indexes):
            del self.shutdown_schedules[idx]
        
        self.save_schedules()  # Save schedules to file            
        
    def save_schedules(self):
        try:
            serializable_schedules = [schedule.isoformat() for schedule in self.shutdown_schedules]
            with open("shutdown_schedules.json", "w") as file:
                json.dump(serializable_schedules, file)
        except Exception as e:
            messagebox.showerror("Error", f"Error saving schedules: {e}")
        
    def show_add_menu(self):
        self.schedule_frame.pack_forget()
        self.add_frame.pack()
        
        hour_label = tk.Label(self.add_frame, text="Hour:", width=10, bg="#2b2b2b", fg="white")
        hour_label.grid(row=0, column=0, padx=10, pady=5)
        
        self.hour_var = tk.StringVar()
        self.hour_dropdown = tk.OptionMenu(self.add_frame, self.hour_var, *range(24))
        self.hour_dropdown.config(width=17, bg="#4d4d4d", fg="white")
        self.hour_dropdown.grid(row=0, column=1, padx=10, pady=5)
        
        minute_label = tk.Label(self.add_frame, text="Minute:", width=10, bg="#2b2b2b", fg="white")
        minute_label.grid(row=1, column=0, padx=10, pady=5)
        
        self.minute_var = tk.StringVar()
        self.minute_dropdown = tk.OptionMenu(self.add_frame, self.minute_var, *range(60))
        self.minute_dropdown.config(width=17, bg="#4d4d4d", fg="white")
        self.minute_dropdown.grid(row=1, column=1, padx=10, pady=5)
        
        confirm_button = tk.Button(self.add_frame, text="Confirm", command=self.add_shutdown, width=20, bg="#ff5722", fg="white")
        confirm_button.grid(row=2, columnspan=2, padx=10, pady=10)
        
    def add_shutdown(self):
        try:
            hour = int(self.hour_var.get())
            minute = int(self.minute_var.get())
            
            shutdown_time = datetime.now().replace(hour=hour, minute=minute, second=0, microsecond=0)
            
            if shutdown_time < datetime.now():
                shutdown_time += timedelta(days=1)
                
            self.shutdown_schedules.append(shutdown_time)
            self.save_schedules()  # Save schedules to file
            
            messagebox.showinfo("Success", f"Shutdown scheduled for {hour:02d}:{minute:02d}")
            
            self.hour_var.set("")  # Reset the dropdown selection
            self.minute_var.set("")  # Reset the dropdown selection
            
            # Reset warning flags
            self.ten_min_warning_shown = False
            self.five_min_warning_shown = False
            
        except ValueError:
            messagebox.showerror("Error", "Invalid hour or minute")
        
    def show_schedule_menu(self):
        self.add_frame.pack_forget()
        self.schedule_frame.pack()
        
        for widget in self.schedule_frame.winfo_children():
            widget.destroy()
        
        now = datetime.now()
        
        upcoming_schedules = [(i, schedule) for i, schedule in enumerate(self.shutdown_schedules) if schedule > now]
        
        if not upcoming_schedules:
            label = tk.Label(self.schedule_frame, text="No upcoming shutdowns", width=30, bg="#2b2b2b", fg="white")
            label.pack(pady=10)
        else:
            for i, (idx, schedule) in enumerate(upcoming_schedules):
                time_remaining = schedule - now
                time_remaining_str = str(time_remaining).split('.')[0]
                label = tk.Label(self.schedule_frame, text=f"Shutdown at {schedule.strftime('%H:%M')} | Time Remaining: {time_remaining_str}", width=40, bg="#2b2b2b", fg="white")
                label.grid(row=i, column=0, padx=10, pady=5)
                
                cancel_button = tk.Button(self.schedule_frame, text="Cancel", command=lambda idx=idx: self.cancel_shutdown(idx), width=10, bg="#ff5722", fg="white")
                cancel_button.grid(row=i, column=1, padx=10, pady=5)
                
                self.timer_updates.append(self.root.after(1000, lambda idx=idx, shutdown_time=schedule: self.update_timer(idx, shutdown_time)))
        
    def update_timer(self, idx, shutdown_time):
        now = datetime.now()
        time_remaining = shutdown_time - now

        if abs(time_remaining.total_seconds() - 600) < 1 and not self.ten_min_warning_shown:
            self.show_auto_close_message("Reminder", "10 minutes remaining until shutdown", 60)
            self.ten_min_warning_shown = True
        elif abs(time_remaining.total_seconds() - 300) < 1 and not self.five_min_warning_shown:
            self.show_auto_close_message("Warning", "5 minutes remaining until shutdown", 60)
            self.five_min_warning_shown = True
        elif abs(time_remaining.total_seconds() - 1) < 1:
            os.system("shutdown -s -t 0")

        time_remaining_str = str(time_remaining).split('.')[0]
        slaves = self.schedule_frame.grid_slaves(row=idx, column=0)
        if slaves:
            label = slaves[0]
            label.config(text=f"Shutdown at {shutdown_time.strftime('%H:%M')} | Time Remaining: {time_remaining_str}")

        self.timer_updates[idx] = self.root.after(1000, lambda: self.update_timer(idx, shutdown_time))
        
    def show_auto_close_message(self, title, message, timeout):
        messagebox_thread = threading.Thread(target=self._show_message_in_thread, args=(title, message, timeout))
        messagebox_thread.start()

    def _show_message_in_thread(self, title, message, timeout):
        dialog = AutoCloseMessageBox(self.root, title, message, timeout)
        dialog.grab_set()
        self.root.wait_window(dialog)
        
    def cancel_shutdown(self, index):
        self.root.after_cancel(self.timer_updates[index])
        del self.shutdown_schedules[index]
        self.save_schedules()  # Save schedules to file
        self.show_schedule_menu()

root = tk.Tk()
app = ShutdownScheduler(root)
root.mainloop()
