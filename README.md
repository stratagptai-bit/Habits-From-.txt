Habit Tracker – Plain Text README

This project is a portable habit tracking system. It uses a single folder named “Habit” to store all files and the executable. Everything the program needs is self-contained inside this folder.

Features:

Daily checklist that loads habits from habits.txt.

Automatic daily rollover that logs progress into progress.txt.

Streak system stored in streaks.txt. Streaks only appear if they are higher than 3 days.

Streak color changes: at 10+ days, a habit button becomes dark blue

Random motivational quote displayed from quotes.txt.

No external libraries required for charts. A simple Tkinter drawing system is used.

Portable .exe. No installation required.

Folder Layout (must look like this):

Habit/
checklist_from_text.exe
habits.txt
quotes.txt
progress.txt
streaks.txt
today.txt
chart_icon.ico
chart_icon.png

The executable must be placed inside the Habit folder or inside a folder directly above it. The program will attempt to locate the Habit folder automatically.

Usage:

Windows: Double-click checklist_from_text.exe to start the application.
The app opens in a maximized window.

Editing Files:

habits.txt – list of habits, one per line
quotes.txt – motivational quotes, one per line
progress.txt – automatically generated daily habit totals
streaks.txt – automatically managed streak counts
today.txt – list of completed habits for today

Building From Source (optional):

Requires Python 3.10 or newer and cx_Freeze installed.

Example build command:

python -m cx_Freeze checklist_from_text.py --target-dir build --base gui --icon chart_icon.ico --exclude-modules matplotlib,numpy,pandas,scipy,dateutil,pytz

Notes:

The application is fully offline and designed to be simple and file-based.
Users can modify the Python file if they want to change behavior.
