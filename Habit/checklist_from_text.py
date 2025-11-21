import tkinter as tk
from tkinter import messagebox
import os
from datetime import datetime
from PIL import Image, ImageTk
import random
import sys
import subprocess

def get_streak(habit_name):
    try:
        with open("streaks.txt", "r", encoding="utf-8") as f:
            lines = f.read().splitlines()
    except FileNotFoundError:
        return 0

    for line in lines:
        if ":" not in line:
            continue

        name, value = line.split(":", 1)
        name = name.strip()
        value = value.strip()

        if name.lower() == habit_name.lower():
            try:
                return int(value)
            except ValueError:
                return 0

    return 0



# === FLEXIBLE SAFE DATA DIRECTORY ===
def find_habit_folder():
    """
    Search upward from the script's location (or executable)
    for a folder named 'Habit'. If found, return its path.
    If not found, show an error and safely exit.
    """
    if getattr(sys, 'frozen', False):
        start_path = os.path.dirname(sys.executable)
    else:
        start_path = os.path.dirname(os.path.abspath(__file__))

    current = start_path
    max_depth = 5  # limit upward traversal to prevent wandering

    for _ in range(max_depth):
        folder_name = os.path.basename(current)
        if folder_name.lower() == "habit":
            return current
        parent = os.path.dirname(current)
        if parent == current:
            break
        current = parent

    # === FAILSAFE: stop safely instead of writing elsewhere ===
    root = tk.Tk()
    root.withdraw()  # hide the window
    messagebox.showerror(
        "Error",
        "The 'Habit' folder could not be found.\n\n"
        "Please make sure the program is inside or below a folder named 'Habit'."
    )
    sys.exit(1)


base_dir = find_habit_folder()
os.makedirs(base_dir, exist_ok=True)

# === FILE PATHS ===
TODAY_FILE = os.path.join(base_dir, "today.txt")
PROGRESS_FILE = os.path.join(base_dir, "progress.txt")
HABITS_FILE = os.path.join(base_dir, "habits.txt")
CHART_ICON_FILE = os.path.join(base_dir, "chart_icon.png")
CHART_ICON_ICO = os.path.join(base_dir, "chart_icon.ico")
QUOTES_FILE = os.path.join(base_dir, "quotes.txt")
STREAKS_FILE = os.path.join(base_dir, "streaks.txt")  # new

# === HELPERS: OPEN FILES ===
def open_file(filepath):
    """Open a text file in the system's default editor."""
    try:
        if os.path.exists(filepath):
            if os.name == "nt":  # Windows
                os.startfile(filepath)
            elif sys.platform == "darwin":  # macOS
                subprocess.Popen(["open", filepath])
            else:  # Linux
                subprocess.Popen(["xdg-open", filepath])
        else:
            messagebox.showwarning("Missing File", f"Could not find {filepath}.")
    except Exception as e:
        messagebox.showerror("Error", f"Failed to open file:\n{e}")


def open_habits_file():
    open_file(HABITS_FILE)


def open_quotes_file():
    open_file(QUOTES_FILE)


# === STREAKS HANDLING ===
def load_streaks():
    """Return dict: {habit: streak_count}"""
    streaks = {}
    if os.path.exists(STREAKS_FILE):
        try:
            with open(STREAKS_FILE, "r", encoding="utf-8") as f:
                for line in f:
                    if ":" in line:
                        habit, count = line.strip().split(":", 1)
                        try:
                            streaks[habit.strip()] = int(count.strip())
                        except:
                            pass
        except Exception:
            # if file read fails, return empty
            return {}
    return streaks


def save_streaks(streaks):
    """Write the streak dict back to the file."""
    try:
        with open(STREAKS_FILE, "w", encoding="utf-8") as f:
            for habit, count in streaks.items():
                f.write(f"{habit}: {count}\n")
    except Exception as e:
        # fail silently but report if running interactive
        try:
            messagebox.showerror("Error", f"Failed to save streaks:\n{e}")
        except:
            pass


def update_streaks(completed_today, all_tasks):
    """
    Update streaks for end of day (Option A):
    - Increment streak for tasks completed yesterday
    - Reset/remove streaks for tasks not completed
    """
    streaks = load_streaks()
    completed_set = set(completed_today)

    new_streaks = {}
    # For tasks in all_tasks: only keep those completed, increment their streak
    for habit in all_tasks:
        if habit in completed_set:
            old = streaks.get(habit, 0)
            new_streaks[habit] = old + 1
        else:
            # habit not completed -> reset (do not include)
            pass

    save_streaks(new_streaks)
    return new_streaks


# === MAIN APP ===
class ChecklistApp:
    def __init__(self, master, tasks, completed_today):
        self.master = master
        master.title("Daily Checklist")
        master.configure(bg="#f0f0f0")

        # === HEADER FRAME (date + chart + edit buttons) ===
        header_frame = tk.Frame(master, bg="#f0f0f0")
        header_frame.pack(fill="x", pady=(10, 0), ipady=15)

        # --- EDIT HABITS BUTTON (top-left corner) ---
        edit_button = tk.Button(
            header_frame,
            text="Edit Habits",
            font=("Arial", 8, "bold"),
            command=open_habits_file,
            bg="#e0e0e0",
            relief="solid",
            bd=1,
            padx=4,
            pady=4,
            cursor="hand2",
            activebackground="#d0d0d0"
        )
        edit_button.place(x=15, y=0, anchor="nw")

        # --- EDIT QUOTES BUTTON (to the right of habits button) ---
        quotes_button = tk.Button(
            header_frame,
            text="Edit Quotes",
            font=("Arial", 8, "bold"),
            command=open_quotes_file,
            bg="#e0e0e0",
            relief="solid",
            bd=1,
            padx=4,
            pady=4,
            cursor="hand2",
            activebackground="#d0d0d0"
        )
        quotes_button.place(x=15, y=35, anchor="nw")

        # --- DATE LABEL (centered) ---
        today_str = datetime.now().strftime("%A, %B %d, %Y")
        date_label = tk.Label(
            header_frame,
            text=f"CURRENT DATE: {today_str}",
            font=("Arial", 20, "bold"),
            bg="#f0f0f0"
        )
        date_label.pack(pady=(0, 0))

        # --- CHART BUTTON (top-right corner) ---
        if os.path.exists(CHART_ICON_FILE):
            try:
                img = Image.open(CHART_ICON_FILE)
                img = img.resize((50, 50), Image.LANCZOS)
                self.chart_icon = ImageTk.PhotoImage(img)
                chart_button = tk.Button(
                    header_frame,
                    image=self.chart_icon,
                    command=self.show_progress_chart,
                    bd=0,
                    bg="#f0f0f0",
                    activebackground="#f0f0f0",
                    cursor="hand2",
                    highlightthickness=0,
                    relief="flat",
                    padx=8,
                    pady=8
                )
                chart_button.place(relx=1.0, x=-25, y=5, anchor="ne")
            except Exception:
                chart_button = tk.Button(
                    header_frame,
                    text="📈",
                    font=("Arial", 20),
                    command=self.show_progress_chart,
                    bd=0,
                    bg="#f0f0f0",
                    activebackground="#f0f0f0",
                    cursor="hand2"
                )
                chart_button.place(relx=1.0, x=-20, y=0, anchor="ne")
        else:
            chart_button = tk.Button(
                header_frame,
                text="📈",
                font=("Arial", 20),
                command=self.show_progress_chart,
                bd=0,
                bg="#f0f0f0",
                activebackground="#f0f0f0",
                cursor="hand2"
            )
            chart_button.place(relx=1.0, x=-20, y=0, anchor="ne")

        # === QUOTE OR INSTRUCTION LABEL ===
        quote_text = ""
        if os.path.exists(QUOTES_FILE):
            try:
                with open(QUOTES_FILE, "r", encoding="utf-8") as f:
                    quotes = [line.strip() for line in f if line.strip()]
                if quotes:
                    quote_text = random.choice(quotes)
            except Exception:
                quote_text = ""

        if not quote_text:
            quote_text = (
                "Tip: Add your habits to 'habits.txt' (one per line) "
                "and your motivational quotes to 'quotes.txt'!"
            )

        quote_label = tk.Label(
            master,
            text=quote_text,
            font=("Arial", 12, "italic"),
            fg="gray30",
            bg="#f0f0f0",
            wraplength=800,
            justify="center"
        )
        quote_label.pack(pady=(0, 15))

        # === STREAK LABEL (bottom-left) ===
        self.streak_label = tk.Label(
            master,
            text="",
            font=("Arial", 12),
            bg="#f0f0f0",
            fg="black",
            justify="left"
        )
        # place it at bottom-left of the window
        self.streak_label.pack(side="bottom", anchor="w", padx=15, pady=(0, 10))

        # === SCROLLABLE CHECKLIST ===
        canvas = tk.Canvas(master, borderwidth=0, background="#f0f0f0", highlightthickness=0)
        scrollbar = tk.Scrollbar(master, orient="vertical", command=canvas.yview)
        canvas.configure(yscrollcommand=scrollbar.set)
        scrollbar.pack(side="right", fill="y")
        canvas.pack(side="left", fill="both", expand=True)

        # Mousewheel scrolling
        def _on_mousewheel(event):
            if event.num == 5 or getattr(event, "delta", 0) < 0:
                canvas.yview_scroll(1, "units")
            elif event.num == 4 or getattr(event, "delta", 0) > 0:
                canvas.yview_scroll(-1, "units")

        canvas.bind_all("<MouseWheel>", _on_mousewheel)
        canvas.bind_all("<Button-4>", _on_mousewheel)
        canvas.bind_all("<Button-5>", _on_mousewheel)

        frame = tk.Frame(canvas, background="#f0f0f0")
        window_id = canvas.create_window((0, 0), window=frame, anchor="n")

        def on_frame_configure(event):
            canvas.configure(scrollregion=canvas.bbox("all"))
        frame.bind("<Configure>", on_frame_configure)

        def on_canvas_configure(event):
            canvas.itemconfigure(window_id, width=event.width)
        canvas.bind("<Configure>", on_canvas_configure)

        frame.grid_columnconfigure(0, weight=1)
        frame.grid_columnconfigure(1, weight=0)
        frame.grid_columnconfigure(2, weight=1)

        self.check_vars = {}
        self.tasks = tasks

        for i, task in enumerate(tasks):
            var = tk.BooleanVar(value=(task in completed_today))

            # --- STREAK COLORING ---
            streak = get_streak(task)
            if streak > 10:
                color = "dark blue"
                print("larger")
            else:
                color = "white"

            cb = tk.Checkbutton(
                frame,
                text=task,
                variable=var,
                onvalue=True,
                offvalue=False,
                font=("Arial", 18),
                indicatoron=False,
                padx=20,
                pady=10,
                command=lambda v=var, t=task: self.toggle_box(v, t),
                bg=color,
                relief="solid",
                bd=1
            )

            cb.grid(row=i, column=1, pady=8)
            self.check_vars[task] = {"var": var, "button": cb}

            if var.get():
                self._mark_complete(cb)



        # Update streak display on start
        self.update_streak_display()

    def toggle_box(self, var, task):
        btn = self.check_vars[task]["button"]
        if var.get():
            self._mark_complete(btn)
            save_completion(task)
        else:
            self._mark_incomplete(btn)
            remove_completion(task)

        # Refresh streak display (streak file only updates at day rollover,
        # but UI keeps consistent with file)
        self.update_streak_display()

    def center_window(self, win):
        win.update_idletasks()
        w = win.winfo_width()
        h = win.winfo_height()
        screen_w = win.winfo_screenwidth()
        screen_h = win.winfo_screenheight()
        x = (screen_w // 2) - (w // 2)
        y = (screen_h // 2) - (h // 2)
        win.geometry(f"{w}x{h}+{x}+{y}")


    def _mark_complete(self, btn):
        btn.config(bg="black", fg="white")

    def _mark_incomplete(self, btn):
        btn.config(bg="white", fg="black")

    def show_progress_chart(self):
        if not os.path.exists(PROGRESS_FILE):
            messagebox.showinfo("No Data", "No progress data found yet.")
            return

        with open(PROGRESS_FILE, "r") as f:
            raw = [line.strip() for line in f]

        data = []
        for line in raw:
            try:
                if line != "":
                    data.append(int(line))
            except ValueError:
                pass

        if len(data) == 0:
            messagebox.showinfo("No Data", "No valid progress entries found.")
            return

        # ---- Window ----
        chart_win = tk.Toplevel(self.master)
        chart_win.title("Habit Progress Over Time")
        chart_win.geometry("800x500")
        self.center_window(chart_win)

        canvas = tk.Canvas(chart_win, bg="white")
        canvas.pack(fill="both", expand=True)

        # ---- Redraw function ----
        def redraw(event=None):
            canvas.delete("all")

            W = canvas.winfo_width()
            H = canvas.winfo_height()
            PAD = int(min(W, H) * 0.08)

            # Axes
            canvas.create_line(PAD, H - PAD, W - PAD, H - PAD, width=2)
            canvas.create_line(PAD, PAD, PAD, H - PAD, width=2)

            # Scaling calculations
            max_y = max(data)
            min_y = min(data)

            if max_y == min_y:
                max_y += 1

            n = len(data)
            x_step = (W - 2 * PAD) / (n - 1 if n > 1 else 1)
            y_scale = (H - 2 * PAD) / (max_y - min_y)

            points = []
            for i, val in enumerate(data):
                x = PAD + i * x_step
                y = H - PAD - (val - min_y) * y_scale
                points.append((x, y))

            # Lines
            for i in range(1, len(points)):
                canvas.create_line(points[i - 1][0], points[i - 1][1],
                                points[i][0], points[i][1], width=2)

            # Dots
            for (x, y) in points:
                canvas.create_oval(x - 4, y - 4, x + 4, y + 4, fill="black")

            # Y-axis labels
            for y_val in range(min_y, max_y + 1):
                y = H - PAD - (y_val - min_y) * y_scale
                canvas.create_text(PAD - 20, y, text=str(y_val), anchor="e")

            # X-axis labels
            for i in range(n):
                x = PAD + i * x_step
                if n <= 15 or i % max(1, n // 15) == 0:
                    canvas.create_text(x, H - PAD + 20, text=str(i + 1))

            # Title
            canvas.create_text(W / 2, PAD / 2, text="Habit Progress Over Time",
                            font=("Arial", int(PAD * 0.4), "bold"))

        # ---- Bind redraw to window resize ----
        canvas.bind("<Configure>", redraw)

        # Initial draw
        redraw()



    def update_streak_display(self):
        streaks = load_streaks()
        display = []

        # Keep the same ordering as tasks
        for habit in self.tasks:
            count = streaks.get(habit, 0)
            if count >= 3:
                display.append(f"{habit}: {count}🔥")

        if display:
            text = "Streaks:\n" + "\n".join(display)
        else:
            text = "Streaks: (no streaks ≥ 3)"

        self.streak_label.config(text=text)


# === DATA HANDLING ===
def load_tasks(filename):
    if not os.path.exists(filename):
        # create empty habits file so user can edit
        with open(filename, "w", encoding="utf-8") as f:
            f.write("")
        return []
    with open(filename, "r", encoding="utf-8") as f:
        return [line.strip() for line in f if line.strip()]


def record_yesterday_progress():
    if not os.path.exists(TODAY_FILE):
        return
    with open(TODAY_FILE, "r", encoding="utf-8") as f:
        lines = [line.strip() for line in f if line.strip()]
    # lines: [date, task1, task2, ...]
    completed_count = max(0, len(lines) - 1)
    with open(PROGRESS_FILE, "a", encoding="utf-8") as pf:
        pf.write(str(completed_count) + "\n")


def ensure_today_file():
    os.makedirs(base_dir, exist_ok=True)
    today_date = datetime.now().strftime("%Y-%m-%d")
    today_obj = datetime.strptime(today_date, "%Y-%m-%d")

    # If today.txt missing → create fresh
    if not os.path.exists(TODAY_FILE):
        with open(TODAY_FILE, "w", encoding="utf-8") as f:
            f.write(today_date + "\n")
        return today_date, []

    # Load existing today.txt
    with open(TODAY_FILE, "r", encoding="utf-8") as f:
        lines = [line.strip() for line in f.readlines() if line.strip()]

    try: 
        stored_date = lines[0]
    except IndexError:
        with open(TODAY_FILE, "w", encoding="utf-8") as f:
            f.write(today_date + "\n")
            stored_date = today_date

    stored_obj = datetime.strptime(stored_date, "%Y-%m-%d")
    day_diff = (today_obj - stored_obj).days

    # === CASE 1 ===
    # Same day → normal load
    if day_diff == 0:
        return today_date, lines[1:]

    # === CASE 2: ONE DAY PASSED (normal rollover) ===
    if day_diff == 1:
        # record yesterday's progress
        record_yesterday_progress()

        # update streaks
        yesterday_completed = lines[1:] if len(lines) > 1 else []
        all_tasks = load_tasks(HABITS_FILE)
        update_streaks(yesterday_completed, all_tasks)

        # reset file for today
        with open(TODAY_FILE, "w", encoding="utf-8") as f:
            f.write(today_date + "\n")
        return today_date, []

    # === CASE 3: MULTIPLE DAYS MISSED ===
    if day_diff > 1:
        missed_days = day_diff - 1  # days between last use and yesterday

        # 1. record "0" for each missed day + yesterday
        # First: record yesterday's real progress
        record_yesterday_progress()

        # Then: append missed days of zeros
        with open(PROGRESS_FILE, "a", encoding="utf-8") as pf:
            for _ in range(missed_days):
                pf.write("0\n")

        # 2. Clear streaks entirely
        with open(STREAKS_FILE, "w", encoding="utf-8") as sf:
            sf.write("")

        # 3. Reset today file fresh
        with open(TODAY_FILE, "w", encoding="utf-8") as f:
            f.write(today_date + "\n")

        return today_date, []



def save_completion(task):
    today_date = datetime.now().strftime("%Y-%m-%d")
    if not os.path.exists(TODAY_FILE):
        with open(TODAY_FILE, "w", encoding="utf-8") as f:
            f.write(today_date + "\n")
    with open(TODAY_FILE, "r", encoding="utf-8") as f:
        lines = [line.strip() for line in f if line.strip()]
    if not lines or lines[0] != today_date:
        with open(TODAY_FILE, "w", encoding="utf-8") as f:
            f.write(today_date + "\n" + task + "\n")
    else:
        completed = set(lines[1:])
        if task not in completed:
            completed.add(task)
            with open(TODAY_FILE, "w", encoding="utf-8") as f:
                f.write(today_date + "\n" + "\n".join(sorted(completed)) + "\n")


def remove_completion(task):
    today_date = datetime.now().strftime("%Y-%m-%d")
    if not os.path.exists(TODAY_FILE):
        return
    with open(TODAY_FILE, "r", encoding="utf-8") as f:
        lines = [line.strip() for line in f if line.strip()]
    if not lines or lines[0] != today_date:
        return
    completed = set(lines[1:])
    if task in completed:
        completed.remove(task)
        with open(TODAY_FILE, "w", encoding="utf-8") as f:
            f.write(today_date + "\n" + "\n".join(sorted(completed)) + "\n")


# === MAIN EXECUTION ===
if __name__ == "__main__":
    root = tk.Tk()

    # Start maximized (not fullscreen)
    try:
        root.state('zoomed')
    except:
        screen_w = root.winfo_screenwidth()
        screen_h = root.winfo_screenheight()
        window_w = int(screen_w * 0.95)
        window_h = int(screen_h * 0.95)
        x_pos = int((screen_w - window_w) / 2)
        y_pos = int((screen_h - window_h) / 2)
        root.geometry(f"{window_w}x{window_h}+{x_pos}+{y_pos}")

    tasks = load_tasks(HABITS_FILE)
    _, completed_today = ensure_today_file()

    app = ChecklistApp(root, tasks, completed_today)
    root.mainloop()
