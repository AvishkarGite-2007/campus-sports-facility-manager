# =====================================================
# FRONTEND - GUI (sidebar layout, dashboard, bookings, fixtures)
# =====================================================
# This file only draws the screens.
# It has NO database code - it asks backend.py for everything.
# numpy is used here to scale the dashboard bar chart
# (and in backend.py to build the points table).
#
# Run this file:   python frontend.py
# (backend.py must be in the same folder)
#
# Optional: put a picture called background.png in the same folder
# and it is shown behind the login box.
# =====================================================

import os
import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime, date, timedelta
import numpy as np
import backend

# ---------- Connect to the database (through the backend) ----------
result = backend.connect()
if result != True:
    print("Could not connect to MySQL:", result)
    input("Press Enter to close...")
    raise SystemExit

# ---------- Colours and fonts ----------
BG = "#f4f6f9"            # page background
CARD = "#ffffff"          # white boxes
BORDER = "#dfe5ec"
SIDEBAR = "#1e2a3a"       # dark menu on the left
ACCENT = "#2f80ed"        # blue
TEXT = "#1f2933"
MUTED = "#6b7785"         # grey text
GREEN = "#1e9e5a"
RED = "#d64545"
ORANGE = "#e08a1e"

F_TITLE = ("Segoe UI", 22, "bold")
F_HEAD = ("Segoe UI", 14, "bold")
F_BODY = ("Segoe UI", 10)
F_BOLD = ("Segoe UI", 10, "bold")

# ---------- Things the program remembers ----------
current_user = ""
content = None            # the frame where each page is drawn
status_label = None       # the message line at the bottom
title_label = None        # the page title in the top bar
nav_buttons = {}          # the sidebar buttons, by name
login_image = None        # keeps the login picture alive

# ---------- Main window ----------
root = tk.Tk()
root.title("Campus Sports Booking")
root.geometry("1100x680")
root.minsize(980, 620)
root.configure(bg=BG)

# ---------- Look of the tables, tabs and drop-downs ----------
style = ttk.Style()
style.theme_use("clam")
style.configure("Treeview", rowheight=28, font=F_BODY, background=CARD,
                fieldbackground=CARD, borderwidth=0)
style.configure("Treeview.Heading", font=F_BOLD, background="#e9eef5",
                foreground=TEXT, relief="flat")
style.map("Treeview", background=[("selected", ACCENT)],
          foreground=[("selected", "white")])
style.configure("TNotebook", background=BG, borderwidth=0)
style.configure("TNotebook.Tab", font=F_BOLD, padding=(16, 6))


# =====================================================
# SMALL HELPERS (used by every page)
# =====================================================
def make_button(parent, text, color, command):
    """A flat coloured button."""
    return tk.Button(parent, text=text, command=command, bg=color, fg="white",
                     activebackground=color, activeforeground="white",
                     font=F_BOLD, relief="flat", bd=0, padx=14, pady=6,
                     cursor="hand2")


def make_card(parent):
    """A white box with a thin border."""
    return tk.Frame(parent, bg=CARD, highlightbackground=BORDER, highlightthickness=1)


def make_table(parent, columns, widths, height=10, left=()):
    """A table (Treeview) with a scrollbar.
    Returns (frame, table). Place the frame; fill the table."""
    holder = tk.Frame(parent, bg=CARD)
    table = ttk.Treeview(holder, columns=columns, show="headings", height=height)
    scroll = ttk.Scrollbar(holder, orient="vertical", command=table.yview)
    table.configure(yscrollcommand=scroll.set)

    for name, width in zip(columns, widths):
        table.heading(name, text=name)
        table.column(name, width=width, anchor="w" if name in left else "center")

    table.pack(side="left", fill="both", expand=True)
    scroll.pack(side="right", fill="y")
    return holder, table


def clear_table(table):
    for item in table.get_children():
        table.delete(item)


def read_date(text):
    """Turns 'YYYY-MM-DD' text into a date. Returns None if it is not a real date."""
    try:
        return datetime.strptime(text.strip(), "%Y-%m-%d").date()
    except ValueError:
        return None


def set_status(message, color=MUTED):
    """Show a short message on the bottom line."""
    status_label.config(text=message, fg=color)


def clear_content():
    for widget in content.winfo_children():
        widget.destroy()


def load_background(width, height):
    """Loads background.png (next to this file) if it exists, otherwise None.
    With Pillow installed (pip install pillow) any picture is resized to fit."""
    path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "background.png")
    if not os.path.exists(path):
        return None
    try:
        from PIL import Image, ImageTk
        return ImageTk.PhotoImage(Image.open(path).resize((width, height)))
    except Exception:
        try:
            return tk.PhotoImage(file=path)
        except Exception:
            return None


# =====================================================
# LOGIN SCREEN
# =====================================================
def show_login():
    global login_image

    for widget in root.winfo_children():
        widget.destroy()
    root.configure(bg=SIDEBAR)

    screen = tk.Frame(root, bg=SIDEBAR)
    screen.pack(fill="both", expand=True)

    # optional picture behind the login box
    login_image = load_background(1100, 680)
    if login_image:
        tk.Label(screen, image=login_image).place(x=0, y=0, relwidth=1, relheight=1)

    box = tk.Frame(screen, bg=CARD, padx=44, pady=34)
    box.place(relx=0.5, rely=0.5, anchor="center")

    tk.Label(box, text="Campus Sports", font=F_TITLE, bg=CARD, fg=ACCENT).pack()
    tk.Label(box, text="Bookings & Fixtures Manager", font=F_BODY, bg=CARD,
             fg=MUTED).pack(pady=(0, 22))

    tk.Label(box, text="Username", font=F_BOLD, bg=CARD, fg=TEXT).pack(anchor="w")
    user_entry = tk.Entry(box, width=32, font=F_BODY, relief="solid", bd=1)
    user_entry.pack(pady=(2, 12), ipady=4)

    tk.Label(box, text="Password", font=F_BOLD, bg=CARD, fg=TEXT).pack(anchor="w")
    pass_entry = tk.Entry(box, width=32, font=F_BODY, relief="solid", bd=1, show="*")
    pass_entry.pack(pady=(2, 6), ipady=4)

    show_password = tk.BooleanVar(value=False)

    def toggle_password():
        pass_entry.config(show="" if show_password.get() else "*")

    tk.Checkbutton(box, text="Show password", variable=show_password,
                   command=toggle_password, bg=CARD, activebackground=CARD,
                   font=F_BODY).pack(anchor="w")

    error_label = tk.Label(box, text="", font=F_BODY, bg=CARD, fg=RED)
    error_label.pack(pady=(8, 0))

    def login(event=None):
        global current_user

        username = user_entry.get().strip()
        password = pass_entry.get().strip()

        if username == "" or password == "":
            error_label.config(text="Enter your username and password.")
            return

        user = backend.check_login(username, password)          # <-- backend

        if user:
            current_user = user
            show_app()
        else:
            error_label.config(text="Wrong username or password.")
            pass_entry.delete(0, "end")

    # pressing Enter in either box also logs in
    user_entry.bind("<Return>", login)
    pass_entry.bind("<Return>", login)

    make_button(box, "Login", ACCENT, login).pack(fill="x", pady=(12, 0))
    user_entry.focus_set()


# =====================================================
# MAIN SCREEN: sidebar + top bar + page area
# =====================================================
def show_app():
    global content, status_label, title_label

    for widget in root.winfo_children():
        widget.destroy()
    root.configure(bg=BG)

    # ----- sidebar (left) -----
    sidebar = tk.Frame(root, bg=SIDEBAR, width=210)
    sidebar.pack(side="left", fill="y")
    sidebar.pack_propagate(False)

    tk.Label(sidebar, text="Campus Sports", font=("Segoe UI", 16, "bold"),
             bg=SIDEBAR, fg="white").pack(pady=(26, 2))
    tk.Label(sidebar, text="Bookings & Fixtures", font=F_BODY, bg=SIDEBAR,
             fg="#9fb3c8").pack(pady=(0, 26))

    nav_buttons.clear()
    for name, page_function in PAGES:
        button = tk.Button(sidebar, text="   " + name, anchor="w", font=("Segoe UI", 11),
                           bg=SIDEBAR, fg="white", activebackground=ACCENT,
                           activeforeground="white", relief="flat", bd=0, padx=10,
                           pady=11, cursor="hand2",
                           command=lambda n=name: open_page(n))
        button.pack(fill="x")
        nav_buttons[name] = button

    tk.Button(sidebar, text="   Logout", anchor="w", font=("Segoe UI", 11),
              bg=SIDEBAR, fg="#ff9d9d", activebackground=RED, activeforeground="white",
              relief="flat", bd=0, padx=10, pady=11, cursor="hand2",
              command=logout).pack(side="bottom", fill="x", pady=16)

    # ----- right side: top bar, message line, page area -----
    main = tk.Frame(root, bg=BG)
    main.pack(side="right", fill="both", expand=True)

    header = tk.Frame(main, bg=CARD, height=62, highlightbackground=BORDER,
                      highlightthickness=1)
    header.pack(fill="x")
    header.pack_propagate(False)

    title_label = tk.Label(header, text="", font=F_HEAD, bg=CARD, fg=TEXT)
    title_label.pack(side="left", padx=24)

    role = "Admin" if current_user == backend.ADMIN_USER else "Student"
    tk.Label(header, text=current_user + "  (" + role + ")", font=F_BOLD,
             bg=CARD, fg=MUTED).pack(side="right", padx=24)

    status_label = tk.Label(main, text="", anchor="w", font=F_BODY, bg=BG, fg=MUTED)
    status_label.pack(side="bottom", fill="x", padx=24, pady=6)

    content = tk.Frame(main, bg=BG)
    content.pack(fill="both", expand=True, padx=24, pady=(16, 0))

    open_page("Dashboard")


def open_page(name):
    """Highlight the sidebar button, then draw that page."""
    for button_name, button in nav_buttons.items():
        button.config(bg=ACCENT if button_name == name else SIDEBAR)

    title_label.config(text=name)
    set_status("")
    clear_content()
    dict(PAGES)[name]()


def logout():
    global current_user
    if messagebox.askyesno("Logout", "Do you want to log out?"):
        current_user = ""
        show_login()


# =====================================================
# DASHBOARD PAGE
# =====================================================
def draw_usage_chart(canvas, usage):
    """Horizontal bar chart. numpy scales all the bars at once."""
    if len(usage) == 0:
        canvas.create_text(10, 20, text="No data yet", anchor="w", fill=MUTED, font=F_BODY)
        return

    names = [row[0] for row in usage]
    counts = np.array([row[1] for row in usage])        # numpy array of the numbers
    longest = max(int(counts.max()), 1)                 # biggest value (at least 1)
    lengths = counts / longest * 220                    # bar length in pixels, all at once

    for i in range(len(names)):
        y = 22 + i * 38
        length = float(lengths[i])
        canvas.create_text(0, y, text=names[i], anchor="w", fill=TEXT, font=F_BODY)
        canvas.create_rectangle(140, y - 11, 140 + length + 2, y + 11, fill=ACCENT, outline="")
        canvas.create_text(140 + length + 10, y, text=str(int(counts[i])), anchor="w",
                           fill=TEXT, font=F_BOLD)


def dashboard_page():
    confirmed, cancelled = backend.get_booking_summary(current_user)    # <-- backend
    upcoming = backend.get_upcoming_fixture_count()                     # <-- backend
    next_match = backend.get_next_fixture()                             # <-- backend

    for column in range(4):
        content.columnconfigure(column, weight=1, uniform="cards")
    content.rowconfigure(1, weight=1)

    def stat_card(column, title, value, color):
        box = make_card(content)
        box.grid(row=0, column=column, sticky="nsew", padx=6, pady=(0, 14))
        tk.Label(box, text=str(value), font=("Segoe UI", 26, "bold"), bg=CARD,
                 fg=color).pack(anchor="w", padx=16, pady=(14, 0))
        tk.Label(box, text=title, font=F_BODY, bg=CARD, fg=MUTED).pack(
            anchor="w", padx=16, pady=(0, 14))

    stat_card(0, "My active bookings", confirmed, GREEN)
    stat_card(1, "My cancelled bookings", cancelled, RED)
    stat_card(2, "Upcoming fixtures", upcoming, ACCENT)

    # fourth card: the next match
    box = make_card(content)
    box.grid(row=0, column=3, sticky="nsew", padx=6, pady=(0, 14))
    if next_match:
        match_text = next_match[0] + " vs " + next_match[1]
        when_text = next_match[2] + "  |  " + next_match[3]
    else:
        match_text = "No match scheduled"
        when_text = "Next match"
    tk.Label(box, text=match_text, font=F_BOLD, bg=CARD, fg=TEXT, wraplength=190,
             justify="left").pack(anchor="w", padx=16, pady=(16, 2))
    tk.Label(box, text=when_text, font=F_BODY, bg=CARD, fg=MUTED, wraplength=190,
             justify="left").pack(anchor="w", padx=16, pady=(0, 14))

    # bar chart (left)
    chart_card = make_card(content)
    chart_card.grid(row=1, column=0, columnspan=2, sticky="nsew", padx=6)
    tk.Label(chart_card, text="Facility usage (bookings + fixtures)", font=F_BOLD,
             bg=CARD, fg=TEXT).pack(anchor="w", padx=16, pady=(14, 0))
    chart = tk.Canvas(chart_card, bg=CARD, highlightthickness=0, height=260)
    chart.pack(fill="both", expand=True, padx=16, pady=10)
    draw_usage_chart(chart, backend.get_facility_usage())               # <-- backend

    # upcoming fixtures (right)
    fixture_card = make_card(content)
    fixture_card.grid(row=1, column=2, columnspan=2, sticky="nsew", padx=6)
    tk.Label(fixture_card, text="Upcoming fixtures", font=F_BOLD, bg=CARD,
             fg=TEXT).pack(anchor="w", padx=16, pady=(14, 0))
    holder, table = make_table(fixture_card, ("Match", "Date"), (210, 100),
                               height=7, left=("Match",))
    holder.pack(fill="both", expand=True, padx=16, pady=10)
    for fixture in backend.get_fixtures("All", "Scheduled")[:6]:        # <-- backend
        table.insert("", "end", values=(fixture[2] + " vs " + fixture[3], fixture[5]))


# =====================================================
# BOOKING PAGE
# =====================================================
def booking_page():
    content.columnconfigure(0, weight=3)
    content.columnconfigure(1, weight=2)

    form = make_card(content)
    form.grid(row=0, column=0, sticky="new", padx=(0, 8))
    side = make_card(content)
    side.grid(row=0, column=1, sticky="new", padx=(8, 0))

    tk.Label(form, text="Book a Facility", font=F_HEAD, bg=CARD, fg=TEXT).grid(
        row=0, column=0, columnspan=2, sticky="w", padx=20, pady=(18, 8))

    def field_label(text, row):
        tk.Label(form, text=text, font=F_BOLD, bg=CARD, fg=TEXT).grid(
            row=row, column=0, sticky="w", padx=20, pady=8)

    # facility
    field_label("Facility", 1)
    facilities = backend.get_facilities()                               # <-- backend
    facility_box = ttk.Combobox(form, values=facilities, state="readonly", width=30)
    if facilities:
        facility_box.current(0)
    facility_box.grid(row=1, column=1, sticky="w", padx=(0, 20))

    # date + quick buttons
    field_label("Date (YYYY-MM-DD)", 2)
    date_entry = tk.Entry(form, width=32, font=F_BODY, relief="solid", bd=1)
    date_entry.insert(0, str(date.today() + timedelta(days=1)))
    date_entry.grid(row=2, column=1, sticky="w", padx=(0, 20), ipady=3)

    quick = tk.Frame(form, bg=CARD)
    quick.grid(row=3, column=1, sticky="w", pady=(0, 4))

    def set_date(days):
        date_entry.delete(0, "end")
        date_entry.insert(0, str(date.today() + timedelta(days=days)))
        refresh_slots()

    for label, days in (("Today", 0), ("Tomorrow", 1), ("In a week", 7)):
        tk.Button(quick, text=label, font=F_BODY, bg="#e9eef5", fg=TEXT, relief="flat",
                  padx=10, cursor="hand2",
                  command=lambda d=days: set_date(d)).pack(side="left", padx=(0, 6))

    # time slot
    field_label("Time Slot", 4)
    time_box = ttk.Combobox(form, values=backend.TIME_SLOTS, state="readonly", width=30)
    time_box.current(0)
    time_box.grid(row=4, column=1, sticky="w", padx=(0, 20))

    # purpose
    field_label("Purpose", 5)
    purpose_entry = tk.Entry(form, width=32, font=F_BODY, relief="solid", bd=1)
    purpose_entry.grid(row=5, column=1, sticky="w", padx=(0, 20), ipady=3)

    # ----- right side: which slots are free? -----
    tk.Label(side, text="Slot availability", font=F_HEAD, bg=CARD, fg=TEXT).pack(
        anchor="w", padx=20, pady=(18, 2))
    availability_note = tk.Label(side, text="", font=F_BODY, bg=CARD, fg=MUTED)
    availability_note.pack(anchor="w", padx=20, pady=(0, 6))

    slot_labels = []
    for slot in backend.TIME_SLOTS:
        slot_label = tk.Label(side, text=slot, anchor="w", font=F_BODY, bg="#eef2f7",
                              fg=MUTED, padx=12, pady=9, cursor="hand2")
        slot_label.pack(fill="x", padx=20, pady=4)
        # clicking a slot picks it in the Time Slot box
        slot_label.bind("<Button-1>", lambda event, s=slot: time_box.set(s))
        slot_labels.append(slot_label)
    tk.Label(side, text="Click a slot to select it.", font=F_BODY, bg=CARD,
             fg=MUTED).pack(anchor="w", padx=20, pady=(4, 18))

    def refresh_slots(event=None):
        chosen = read_date(date_entry.get())
        if chosen is None:
            availability_note.config(text="Enter a valid date to see availability.")
            for i, slot in enumerate(backend.TIME_SLOTS):
                slot_labels[i].config(text=slot, bg="#eef2f7", fg=MUTED)
            return

        availability_note.config(text=facility_box.get() + " on " + chosen.strftime("%d %b %Y"))
        for i, slot in enumerate(backend.TIME_SLOTS):
            if backend.is_slot_taken(facility_box.get(), chosen, slot):         # <-- backend
                slot_labels[i].config(text=slot + "   -   Booked", bg="#fde8e8", fg=RED)
            else:
                slot_labels[i].config(text=slot + "   -   Available", bg="#e3f6ea", fg=GREEN)

    facility_box.bind("<<ComboboxSelected>>", refresh_slots)
    date_entry.bind("<KeyRelease>", refresh_slots)

    def save():
        facility = facility_box.get()
        time_slot = time_box.get()
        purpose = purpose_entry.get().strip()
        chosen = read_date(date_entry.get())

        if facility == "" or time_slot == "":
            messagebox.showwarning("Missing details", "Select a facility and a time slot.")
            return
        if chosen is None:
            messagebox.showwarning("Wrong date", "Write the date like this: 2026-10-15")
            return
        if chosen < date.today():
            messagebox.showwarning("Wrong date", "You cannot book a past date.")
            return
        if purpose == "":
            messagebox.showwarning("Missing details", "Please enter a purpose.")
            return
        if backend.is_slot_taken(facility, chosen, time_slot):                  # <-- backend
            messagebox.showwarning("Slot taken", "That slot is already booked.")
            refresh_slots()
            return

        backend.add_booking(current_user, facility, chosen, time_slot, purpose)  # <-- backend

        open_page("My Bookings")
        set_status("Booking saved: " + facility + ", " + chosen.strftime("%d %b %Y")
                   + ", " + time_slot, GREEN)

    make_button(form, "Confirm Booking", GREEN, save).grid(
        row=6, column=0, columnspan=2, sticky="w", padx=20, pady=(14, 22))

    refresh_slots()


# =====================================================
# MY BOOKINGS PAGE
# =====================================================
def bookings_page():
    rows = backend.get_bookings(current_user)                                   # <-- backend

    content.columnconfigure(0, weight=1)
    content.rowconfigure(1, weight=1)

    # top line: filter + count
    top_bar = tk.Frame(content, bg=BG)
    top_bar.grid(row=0, column=0, sticky="ew", pady=(0, 10))
    tk.Label(top_bar, text="Show:", font=F_BOLD, bg=BG, fg=TEXT).pack(side="left")
    filter_box = ttk.Combobox(top_bar, values=["All", "Confirmed", "Cancelled"],
                              state="readonly", width=12)
    filter_box.current(0)
    filter_box.pack(side="left", padx=8)
    count_label = tk.Label(top_bar, text="", font=F_BODY, bg=BG, fg=MUTED)
    count_label.pack(side="left", padx=10)

    # table
    card = make_card(content)
    card.grid(row=1, column=0, sticky="nsew")
    holder, table = make_table(card, ("ID", "Facility", "Date", "Time", "Purpose", "Status"),
                               (50, 170, 110, 170, 220, 100), height=14,
                               left=("Facility", "Purpose"))
    holder.pack(fill="both", expand=True, padx=2, pady=2)
    table.tag_configure("Confirmed", foreground=GREEN)
    table.tag_configure("Cancelled", foreground=MUTED)

    def fill_table(event=None):
        clear_table(table)
        shown = 0
        for row in rows:
            if filter_box.get() != "All" and row[5] != filter_box.get():
                continue
            table.insert("", "end", iid=str(row[0]), values=row, tags=(row[5],))
            shown += 1
        count_label.config(text=str(shown) + " booking(s)")

    filter_box.bind("<<ComboboxSelected>>", fill_table)
    fill_table()

    def cancel():
        selected = table.selection()
        if not selected:
            messagebox.showwarning("Nothing selected", "Click a booking first.")
            return
        if table.set(selected[0], "Status") == "Cancelled":
            messagebox.showinfo("Already cancelled", "This booking is already cancelled.")
            return
        if not messagebox.askyesno("Cancel booking", "Cancel this booking?"):
            return

        backend.cancel_booking(int(selected[0]), current_user)                  # <-- backend

        open_page("My Bookings")
        set_status("Booking cancelled.", ORANGE)

    button_row = tk.Frame(content, bg=BG)
    button_row.grid(row=2, column=0, sticky="w", pady=12)
    make_button(button_row, "Cancel Selected Booking", RED, cancel).pack(side="left")


# =====================================================
# FIXTURES PAGE (team matches, results, points table)
# =====================================================
def fixtures_page():
    is_admin = (current_user == backend.ADMIN_USER)
    sports = backend.get_sports()                                               # <-- backend

    content.columnconfigure(0, weight=1)
    content.rowconfigure(0, weight=1)

    tabs = ttk.Notebook(content)
    tabs.grid(row=0, column=0, sticky="nsew")
    fixtures_tab = tk.Frame(tabs, bg=BG)
    points_tab = tk.Frame(tabs, bg=BG)
    tabs.add(fixtures_tab, text="  Fixtures & Results  ")
    tabs.add(points_tab, text="  Points Table  ")

    # ================= TAB 1: fixtures list =================
    fixtures_tab.columnconfigure(0, weight=1)
    fixtures_tab.rowconfigure(1, weight=1)

    bar = tk.Frame(fixtures_tab, bg=BG)
    bar.grid(row=0, column=0, sticky="ew", padx=8, pady=10)
    tk.Label(bar, text="Sport:", font=F_BOLD, bg=BG, fg=TEXT).pack(side="left")
    sport_filter = ttk.Combobox(bar, values=["All"] + sports, state="readonly", width=14)
    sport_filter.current(0)
    sport_filter.pack(side="left", padx=8)
    count_label = tk.Label(bar, text="", font=F_BODY, bg=BG, fg=MUTED)
    count_label.pack(side="left", padx=10)

    card = make_card(fixtures_tab)
    card.grid(row=1, column=0, sticky="nsew", padx=8)
    holder, table = make_table(
        card, ("ID", "Sport", "Match", "Venue", "Date", "Time", "Result", "Status"),
        (40, 90, 230, 130, 100, 150, 70, 90), height=9, left=("Match",))
    holder.pack(fill="both", expand=True, padx=2, pady=2)
    table.tag_configure("Scheduled", foreground=ACCENT)
    table.tag_configure("Completed", foreground=GREEN)

    def fill_fixtures(event=None):
        clear_table(table)
        fixtures = backend.get_fixtures(sport_filter.get())                     # <-- backend
        for f in fixtures:
            # f = (id, sport, team1, team2, venue, date, time, score1, score2, status)
            result_text = "-"
            if f[7] is not None and f[8] is not None:
                result_text = str(f[7]) + " - " + str(f[8])
            table.insert("", "end", iid=str(f[0]),
                         values=(f[0], f[1], f[2] + " vs " + f[3], f[4], f[5], f[6],
                                 result_text, f[9]),
                         tags=(f[9],))
        count_label.config(text=str(len(fixtures)) + " fixture(s)")

    sport_filter.bind("<<ComboboxSelected>>", fill_fixtures)

    # ----- admin tools (only the admin sees these) -----
    if is_admin:
        admin = tk.LabelFrame(fixtures_tab, text="  Admin tools  ", font=F_BOLD, bg=BG,
                              fg=TEXT, padx=12, pady=8)
        admin.grid(row=2, column=0, sticky="ew", padx=8, pady=10)

        # row 0 = small labels, row 1 = the boxes
        for column, text in enumerate(("Sport", "Team 1", "Team 2", "Ground", "Date", "Time")):
            tk.Label(admin, text=text, font=F_BODY, bg=BG, fg=MUTED).grid(
                row=0, column=column, sticky="w", padx=4)

        new_sport = ttk.Combobox(admin, values=sports, state="readonly", width=12)
        new_sport.grid(row=1, column=0, padx=4)
        team1_box = ttk.Combobox(admin, values=[], state="readonly", width=17)
        team1_box.grid(row=1, column=1, padx=4)
        team2_box = ttk.Combobox(admin, values=[], state="readonly", width=17)
        team2_box.grid(row=1, column=2, padx=4)
        ground_label = tk.Label(admin, text="-", font=F_BODY, bg=BG, fg=TEXT, width=16,
                                anchor="w")
        ground_label.grid(row=1, column=3, padx=4)
        new_date = tk.Entry(admin, width=12, font=F_BODY, relief="solid", bd=1)
        new_date.insert(0, str(date.today() + timedelta(days=1)))
        new_date.grid(row=1, column=4, padx=4, ipady=2)
        new_time = ttk.Combobox(admin, values=backend.TIME_SLOTS, state="readonly", width=19)
        new_time.current(0)
        new_time.grid(row=1, column=5, padx=4)

        def on_sport_chosen(event=None):
            teams = backend.get_teams(new_sport.get())                          # <-- backend
            team1_box["values"] = teams
            team2_box["values"] = teams
            team1_box.set("")
            team2_box.set("")
            ground_label.config(text=backend.SPORT_FACILITY.get(new_sport.get(), "-"))

        new_sport.bind("<<ComboboxSelected>>", on_sport_chosen)
        if sports:
            new_sport.current(0)
            on_sport_chosen()

        def schedule():
            sport = new_sport.get()
            team1 = team1_box.get()
            team2 = team2_box.get()
            slot = new_time.get()
            chosen = read_date(new_date.get())
            ground = backend.SPORT_FACILITY.get(sport)

            if sport == "" or team1 == "" or team2 == "":
                messagebox.showwarning("Missing details", "Choose a sport and both teams.")
                return
            if team1 == team2:
                messagebox.showwarning("Wrong teams", "A team cannot play against itself.")
                return
            if ground is None:
                messagebox.showwarning("No ground", "No ground is set for " + sport + ".")
                return
            if chosen is None:
                messagebox.showwarning("Wrong date", "Write the date like this: 2026-10-15")
                return
            if chosen < date.today():
                messagebox.showwarning("Wrong date", "You cannot schedule a past date.")
                return
            if backend.is_slot_taken(ground, chosen, slot):                     # <-- backend
                messagebox.showwarning("Slot taken", ground + " is already used in that slot.")
                return

            backend.add_fixture(sport, team1, team2, ground, chosen, slot)      # <-- backend
            fill_fixtures()
            set_status("Fixture scheduled: " + team1 + " vs " + team2, GREEN)

        make_button(admin, "Schedule Fixture", ACCENT, schedule).grid(
            row=1, column=6, padx=(12, 4))

        # result + delete
        result_row = tk.Frame(admin, bg=BG)
        result_row.grid(row=2, column=0, columnspan=7, sticky="w", pady=(12, 0))
        tk.Label(result_row, text="Click a fixture above, then enter its score:",
                 font=F_BODY, bg=BG, fg=MUTED).pack(side="left", padx=(4, 10))
        score1 = tk.Entry(result_row, width=5, justify="center", font=F_BOLD,
                          relief="solid", bd=1)
        score1.pack(side="left", ipady=2)
        tk.Label(result_row, text=" - ", font=F_BOLD, bg=BG, fg=TEXT).pack(side="left")
        score2 = tk.Entry(result_row, width=5, justify="center", font=F_BOLD,
                          relief="solid", bd=1)
        score2.pack(side="left", ipady=2)

        def save_score():
            selected = table.selection()
            if not selected:
                messagebox.showwarning("Nothing selected", "Click a fixture in the table first.")
                return
            try:
                points1 = int(score1.get())
                points2 = int(score2.get())
            except ValueError:
                messagebox.showwarning("Wrong score", "Scores must be whole numbers.")
                return
            if points1 < 0 or points2 < 0:
                messagebox.showwarning("Wrong score", "Scores cannot be negative.")
                return

            backend.save_result(int(selected[0]), points1, points2)             # <-- backend
            score1.delete(0, "end")
            score2.delete(0, "end")
            fill_fixtures()
            fill_points()
            set_status("Result saved. The points table is updated.", GREEN)

        def remove_fixture():
            selected = table.selection()
            if not selected:
                messagebox.showwarning("Nothing selected", "Click a fixture in the table first.")
                return
            if not messagebox.askyesno("Delete fixture", "Delete the selected fixture?"):
                return

            backend.delete_fixture(int(selected[0]))                            # <-- backend
            fill_fixtures()
            fill_points()
            set_status("Fixture deleted.", ORANGE)

        make_button(result_row, "Save Result", GREEN, save_score).pack(side="left", padx=10)
        make_button(result_row, "Delete Fixture", RED, remove_fixture).pack(side="left")
    else:
        tk.Label(fixtures_tab, text="Only the admin can schedule fixtures and enter results.",
                 font=F_BODY, bg=BG, fg=MUTED).grid(row=2, column=0, sticky="w",
                                                    padx=12, pady=10)

    # ================= TAB 2: points table =================
    points_tab.columnconfigure(0, weight=1)
    points_tab.rowconfigure(1, weight=1)

    bar2 = tk.Frame(points_tab, bg=BG)
    bar2.grid(row=0, column=0, sticky="ew", padx=8, pady=10)
    tk.Label(bar2, text="Sport:", font=F_BOLD, bg=BG, fg=TEXT).pack(side="left")
    points_sport = ttk.Combobox(bar2, values=sports, state="readonly", width=14)
    if sports:
        points_sport.current(0)
    points_sport.pack(side="left", padx=8)
    tk.Label(bar2, text="Win = 3 points, draw = 1 point, loss = 0",
             font=F_BODY, bg=BG, fg=MUTED).pack(side="left", padx=14)

    card2 = make_card(points_tab)
    card2.grid(row=1, column=0, sticky="nsew", padx=8)
    holder2, points_table = make_table(
        card2, ("Pos", "Team", "P", "W", "D", "L", "For", "Against", "Diff", "Pts"),
        (50, 220, 50, 50, 50, 50, 70, 80, 60, 60), height=10, left=("Team",))
    holder2.pack(fill="both", expand=True, padx=2, pady=2)
    points_table.tag_configure("leader", foreground=GREEN, font=F_BOLD)

    def fill_points(event=None):
        clear_table(points_table)
        if points_sport.get() == "":
            return
        for row in backend.get_standings(points_sport.get()):                   # <-- backend (numpy)
            leader = row[0] == 1 and row[2] > 0        # first place, and has played
            points_table.insert("", "end", values=row,
                                tags=("leader",) if leader else ())

    points_sport.bind("<<ComboboxSelected>>", fill_points)
    tabs.bind("<<NotebookTabChanged>>", fill_points)

    fill_fixtures()
    fill_points()


# =====================================================
# START THE PROGRAM
# =====================================================
# (names of the pages, in sidebar order)
PAGES = [
    ("Dashboard", dashboard_page),
    ("Book Facility", booking_page),
    ("My Bookings", bookings_page),
    ("Fixtures", fixtures_page),
]


def on_close():
    backend.close()
    root.destroy()


root.protocol("WM_DELETE_WINDOW", on_close)
show_login()
root.mainloop()