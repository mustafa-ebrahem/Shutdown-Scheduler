# Shutdown Scheduler

Shutdown Scheduler is a desktop application built with Python and Tkinter that allows users to schedule automatic shutdowns for their computer.

## Features

- Schedule shutdowns at specific times
- View and manage upcoming scheduled shutdowns
- Automatic reminders at 10 minutes and 5 minutes before shutdown
- Dark mode user interface for comfortable use in low-light environments
- Persistent storage of scheduled shutdowns

## Requirements

- Python 3.x
- Tkinter (usually comes pre-installed with Python)

## Installation

1. Clone this repository or download the source code.
2. Ensure you have Python 3.x installed on your system.

## Usage

1. Run the script using Python:

   ```
   python shutdown_scheduler.py
   ```

2. The main window will appear, showing two options: "Add" and "Schedule".

3. To add a new shutdown:
   - Click the "Add" button
   - Set the desired hour and minute for the shutdown
   - Click "Confirm" to schedule the shutdown

4. To view or cancel scheduled shutdowns:
   - Click the "Schedule" button
   - You'll see a list of upcoming shutdowns with their scheduled time and remaining time
   - To cancel a shutdown, click the "Cancel" button next to it

5. The application will show warning messages:
   - 10 minutes before shutdown
   - 5 minutes before shutdown

6. The system will automatically shut down at the scheduled time

## Persistent Storage

The application uses a JSON file (`shutdown_schedules.json`) to store scheduled shutdowns. This file will be created automatically in the same directory as the script when you first schedule a shutdown.

## Customization

You can modify the warning times by adjusting the values in the `update_timer` method of the `ShutdownScheduler` class.

## Note

This application uses the Windows `shutdown` command to perform the system shutdown. If you're using a different operating system, you may need to modify the shutdown command in the `update_timer` method.

## Troubleshooting

If you encounter any issues with scheduling or executing shutdowns, ensure that:
- You have the necessary permissions to shut down your computer
- The system time is set correctly
- The `shutdown_schedules.json` file is not corrupted (you can delete it to start fresh if needed)

## Contributing

Contributions, bug reports, and feature requests are welcome! Feel free to submit issues or pull requests to improve the application.

## License

This project is open-source and available under the MIT License.
