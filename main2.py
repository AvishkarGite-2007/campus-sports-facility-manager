
from tkinter import *
from tkinter import ttk, messagebox
from datetime import datetime, date, timedelta
import backend


top = Tk()
top.withdraw()                                   

result = backend.connect()
if result is not True:                          
    messagebox.showerror("Database Connection Error", str(result))
    top.destroy()
    raise SystemExit

top.title("Campus Sports Booking")
top.geometry("1100x700")
top.minsize(1000, 650)
top.deiconify()                                  

current_user = ""                                

# Colours and fonts 
BG = "#0f172a"           # page background
SIDEBAR = "#162033"      # menu on the left
CARD = "#1e293b"         # boxes
INPUT_BG = "#334155"     # typing boxes
TEXT = "#f8fafc"         # white text
MUTED = "#94a3b8"        # grey text
GREEN = "#22c55e"
BLUE = "#3b82f6"
RED = "#ef4444"
BOOKED = "#f87171"      
F_TITLE = ("Segoe UI", 22, "bold")
F_BODY = ("Segoe UI", 12)
F_BOLD = ("Segoe UI", 12, "bold")
F_SMALL = ("Segoe UI", 10, "bold")

top.configure(bg=BG)

style = ttk.Style(top)
style.theme_use("clam")
style.configure("Treeview", background=CARD, fieldbackground=CARD, foreground=TEXT,
                rowheight=36, borderwidth=0, font=("Segoe UI", 11))
style.configure("Treeview.Heading", background=SIDEBAR, foreground=MUTED,
                font=("Segoe UI", 11, "bold"), relief="flat", padding=8)
style.map("Treeview", background=[("selected", BLUE)], foreground=[("selected", TEXT)])
style.map("TCombobox", fieldbackground=[("readonly", INPUT_BG)],
          foreground=[("readonly", TEXT)])
top.option_add("*TCombobox*Listbox.font", ("Segoe UI", 12))

menu = Frame(top, bg=SIDEBAR, width=240)
menu.pack_propagate(False)
page = Frame(top, bg=BG)
page.pack(side="right", fill="both", expand=True)

nav_buttons = {}                                



def make_label(parent, text, font=F_BODY, color=TEXT, bg=CARD):
    return Label(parent, text=text, font=font, fg=color, bg=bg)


def make_button(parent, text, color, command, fg="white"):
    return Button(parent, text=text, command=command, font=F_BOLD, bg=color, fg=fg,
                  activebackground=color, activeforeground=fg, relief="flat",
                  padx=14, pady=8, cursor="hand2")


def make_entry(parent, **extra):
    return Entry(parent, font=F_BODY, bg=INPUT_BG, fg=TEXT, insertbackground=TEXT,
                 relief="flat", **extra)


def make_listbox(parent, height):
    return Listbox(parent, height=height, font=F_BODY, bg=INPUT_BG, fg=TEXT,
                   selectbackground=BLUE, selectforeground="white", relief="flat",
                   highlightthickness=0, exportselection=0, activestyle="none")


def make_combo(parent, values, width):
    return ttk.Combobox(parent, values=values, width=width, font=F_BODY, state="readonly")


def make_table(parent, columns, widths):
    """A table with a scrollbar. Returns (frame, table)."""
    frame = Frame(parent, bg=CARD)
    table = ttk.Treeview(frame, columns=columns, show="headings", selectmode="browse")
    for name, width in zip(columns, widths):
        table.heading(name, text=name.upper())
        table.column(name, width=width, anchor="center")
    scroll = ttk.Scrollbar(frame, orient="vertical", command=table.yview)
    table.configure(yscrollcommand=scroll.set)
    table.pack(side="left", fill="both", expand=True)
    scroll.pack(side="right", fill="y")
    return frame, table


def read_date(text):
    """Turns '2026-11-05' into a date. Gives None if it is not a real date."""
    try:
        return datetime.strptime(text.strip(), "%Y-%m-%d").date()
    except ValueError:
        return None


def show_error(error, title="Error", parent=None):
    """ValueError = a rule from the backend (e.g. slot taken). Anything else = database problem."""
    if isinstance(error, ValueError):
        messagebox.showwarning(title, str(error), parent=parent)
    else:
        messagebox.showerror("Database Error", str(error), parent=parent)


def clear():
    """Remove everything from the page area."""
    for widget in page.winfo_children():
        widget.destroy()


def page_header(title, subtitle):
    box = Frame(page, bg=BG)
    box.pack(fill="x", padx=28, pady=(24, 14))
    make_label(box, title, F_TITLE, bg=BG).pack(anchor="w")
    make_label(box, subtitle, F_BODY, MUTED, BG).pack(anchor="w")


def highlight_nav(active):
    for key, button in nav_buttons.items():
        if key == active:
            button.config(bg=CARD, fg=GREEN)
        else:
            button.config(bg=SIDEBAR, fg=TEXT)


# =====================================================
# MENU ON THE LEFT
# =====================================================
def setup_menu():
    nav_buttons.clear()
    for widget in menu.winfo_children():
        widget.destroy()

    # ----- top: logo and name -----
    logo = Frame(menu, bg=SIDEBAR)
    logo.pack(fill="x", padx=22, pady=(28, 18))
    make_label(logo, "🏆", ("Segoe UI", 28), GREEN, SIDEBAR).pack(anchor="w")
    make_label(logo, "Campus Sports", ("Segoe UI", 16, "bold"), TEXT, SIDEBAR).pack(anchor="w")
    make_label(logo, "Bookings & Fixtures", F_SMALL, MUTED, SIDEBAR).pack(anchor="w")

    Frame(menu, bg=INPUT_BG, height=1).pack(fill="x", padx=22, pady=(0, 14))   # thin line
    make_label(menu, "MENU", F_SMALL, MUTED, SIDEBAR).pack(anchor="w", padx=24, pady=(0, 6))

    # ----- the page buttons -----
    items = [
        ("🏠   Dashboard", "Dashboard", dashboard_page),
        ("📅   Book Facility", "Book", booking_page),
        ("📋   My Bookings", "Bookings", bookings_page),
        ("🏆   Fixtures", "Fixtures", fixtures_page),
    ]
    for text, key, command in items:
        button = Button(menu, text=text, command=command, font=F_BODY, bg=SIDEBAR,
                        fg=TEXT, activebackground=CARD, activeforeground=GREEN,
                        relief="flat", anchor="w", padx=18, pady=11, cursor="hand2")
        button.pack(fill="x", padx=12, pady=2)
        nav_buttons[key] = button

    Frame(menu, bg=SIDEBAR).pack(expand=True, fill="both")     

    # ----- bottom: who is logged in + logout -----
    who = "Admin" if current_user == backend.ADMIN_USER else "Student"
    user_box = Frame(menu, bg=CARD, padx=14, pady=10)
    user_box.pack(fill="x", padx=12, pady=(0, 10))
    make_label(user_box, "Logged in as", F_SMALL, MUTED).pack(anchor="w")
    make_label(user_box, "👤 " + current_user, F_BOLD).pack(anchor="w")
    make_label(user_box, who, F_SMALL, GREEN).pack(anchor="w")

    Button(menu, text="🚪  Logout", command=logout, font=F_BOLD, bg=RED, fg="white",
           activebackground=RED, activeforeground="white", relief="flat", pady=10,
           cursor="hand2").pack(fill="x", padx=12, pady=(0, 20))


def logout():
    global current_user
    current_user = ""
    menu.pack_forget()
    login_page()



# LOGIN PAGE

def login_page():
    clear()
    box = Frame(page, bg=CARD, padx=40, pady=32)
    box.place(relx=0.5, rely=0.5, anchor="center")
    make_label(box, "🏆", ("Segoe UI", 40), GREEN).pack()
    make_label(box, "Campus Sports Manager", F_TITLE).pack(pady=(4, 4))
    make_label(box, "Sign in to book facilities and view fixtures", F_BODY, MUTED).pack(
        pady=(0, 22))
    make_label(box, "USERNAME", F_SMALL, MUTED).pack(anchor="w")
    user_entry = make_entry(box, width=28)
    user_entry.pack(fill="x", ipady=7, pady=(4, 14))
    make_label(box, "PASSWORD", F_SMALL, MUTED).pack(anchor="w")
    pass_entry = make_entry(box, width=28, show="•")
    pass_entry.pack(fill="x", ipady=7, pady=(4, 22))
    def login(event=None):
        global current_user
        username = user_entry.get().strip()
        password = pass_entry.get().strip()
        if username == "" or password == "":
            messagebox.showwarning("Missing Details", "Enter your username and password.")
            return
        try:
            user = backend.check_login(username, password)         
        except Exception as error:
            show_error(error, "Login Error")
            return
        if user:
            current_user = user
            setup_menu()
            menu.pack(side="left", fill="y")
            dashboard_page()
        else:
            messagebox.showerror("Login Failed", "Incorrect username or password.")
            pass_entry.delete(0, END)
    user_entry.bind("<Return>", login)               
    pass_entry.bind("<Return>", login)
    make_button(box, "Login  →", GREEN, login, fg="#052e16").pack(fill="x")
    user_entry.focus_set()


# DASHBOARD PAGE
def dashboard_page():
    clear()
    highlight_nav("Dashboard")
    page_header("Welcome, " + current_user + "! 👋", "Overview of your campus sports reservations")

    try:
        active = backend.count_active_bookings(current_user)       
        total = len(backend.get_bookings(current_user))
        venues = len(backend.get_facilities())
        upcoming = backend.get_upcoming_fixture_count()
    except Exception as error:
        show_error(error)
        return

    # ----- four number boxes in a row -----
    row = Frame(page, bg=BG)
    row.pack(fill="x", padx=23, pady=(0, 24))

    boxes = [
        ("ACTIVE BOOKINGS", active, GREEN),
        ("AVAILABLE VENUES", venues, BLUE),
        ("TOTAL REQUESTS", total, "#a855f7"),
        ("UPCOMING FIXTURES", upcoming, "#f59e0b"),
    ]
    for number, (title, value, color) in enumerate(boxes):
        row.grid_columnconfigure(number, weight=1, uniform="boxes")
        box = Frame(row, bg=CARD, padx=14, pady=16)
        box.grid(row=0, column=number, padx=5, sticky="nsew")
        make_label(box, title, F_SMALL, MUTED).pack(anchor="w")
        make_label(box, str(value), ("Segoe UI", 28, "bold"), color).pack(anchor="w", pady=6)

    # ----- shortcut buttons -----
    buttons = Frame(page, bg=BG)
    buttons.pack(anchor="w", padx=28)
    make_button(buttons, "+ Book a Facility", GREEN, booking_page, fg="#052e16").pack(
        side="left")
    make_button(buttons, "View Fixtures", BLUE, fixtures_page).pack(side="left", padx=8)


 
# BOOK FACILITY PAGE
def booking_page():
    clear()
    highlight_nav("Book")
    page_header("Book a Facility", "Choose a facility, date, time slot, and purpose")

    form = Frame(page, bg=CARD, padx=24, pady=20)
    form.pack(fill="both", expand=True, padx=28, pady=(0, 24))
    form.grid_columnconfigure(0, weight=1, uniform="half")
    form.grid_columnconfigure(1, weight=1, uniform="half")


    left = Frame(form, bg=CARD)
    left.grid(row=0, column=0, sticky="nsew", padx=(0, 12))

    make_label(left, "SELECT FACILITY", F_SMALL, MUTED).pack(anchor="w", pady=(0, 6))
    facility_box = make_listbox(left, 7)
    facilities = backend.get_facilities()                          
    for name in facilities:
        facility_box.insert(END, name)
    facility_box.pack(fill="x")


    right = Frame(form, bg=CARD)
    right.grid(row=0, column=1, sticky="nsew", padx=(12, 0))

    make_label(right, "DATE (YYYY-MM-DD)", F_SMALL, MUTED).pack(anchor="w", pady=(0, 5))
    date_entry = make_entry(right)
    date_entry.insert(0, str(date.today() + timedelta(days=1)))
    date_entry.pack(fill="x", ipady=6, pady=(0, 12))

    make_label(right, "SELECT TIME SLOT  (red = already booked)", F_SMALL, MUTED).pack(
        anchor="w", pady=(0, 6))
    time_box = make_listbox(right, len(backend.TIME_SLOTS))
    for slot in backend.TIME_SLOTS:
        time_box.insert(END, slot)
    time_box.pack(fill="x", pady=(0, 12))

    make_label(right, "PURPOSE", F_SMALL, MUTED).pack(anchor="w", pady=(0, 5))
    purpose_entry = make_entry(right)
    purpose_entry.pack(fill="x", ipady=6)

    def chosen_facility():
        picked = facility_box.curselection()
        if picked:
            return facility_box.get(picked[0])
        return ""

    def show_taken_slots(event=None):
        """Paint the slots that are already booked red."""
        facility = chosen_facility()
        day = read_date(date_entry.get())

        taken = []
        if facility != "" and day is not None:
            taken = backend.get_taken_slots(facility, day)          

        for number, slot in enumerate(backend.TIME_SLOTS):
            if slot in taken:
                time_box.itemconfig(number, foreground=BOOKED)
            else:
                time_box.itemconfig(number, foreground=TEXT)

    facility_box.bind("<<ListboxSelect>>", show_taken_slots)       
    date_entry.bind("<KeyRelease>", show_taken_slots)              

    def save():
        facility = chosen_facility()
        picked_slot = time_box.curselection()
        purpose = purpose_entry.get().strip()
        day = read_date(date_entry.get())

        if facility == "":
            messagebox.showwarning("Missing Facility", "Select a facility.")
            return
        if not picked_slot:
            messagebox.showwarning("Missing Time", "Select a time slot.")
            return
        if day is None:
            messagebox.showwarning("Invalid Date", "Enter the date as YYYY-MM-DD.")
            return
        if day < date.today():
            messagebox.showwarning("Invalid Date", "You cannot book a past date.")
            return
        if purpose == "":
            messagebox.showwarning("Missing Purpose", "Enter the purpose of your booking.")
            return

        slot = time_box.get(picked_slot[0])
        try:
            backend.add_booking(current_user, facility, day, slot, purpose)   # <-- backend
        except Exception as error:
            show_error(error, "Slot Unavailable")
            show_taken_slots()
            return

        messagebox.showinfo("Success", "Booking saved successfully.")
        bookings_page()

    make_button(form, "✔  Confirm Booking", GREEN, save, fg="#052e16").grid(
        row=1, column=0, columnspan=2, sticky="e", pady=(18, 0))

    if facilities:
        facility_box.selection_set(0)
    show_taken_slots()


 
# MY BOOKINGS PAGE
def bookings_page():
    clear()
    highlight_nav("Bookings")
    page_header("My Bookings", "Select a reservation if you want to cancel it")

    try:
        rows = backend.get_bookings(current_user)                   # <-- backend
    except Exception as error:
        show_error(error)
        return

    frame, table = make_table(page, ("Facility", "Date", "Time Slot", "Purpose", "Status"),
                              (190, 130, 200, 220, 120))
    frame.pack(fill="both", expand=True, padx=28, pady=(0, 12))
    table.tag_configure("Confirmed", foreground=GREEN)
    table.tag_configure("Cancelled", foreground=RED)

    for number, row in enumerate(rows):
        table.insert("", END, iid=str(number), values=row[1:], tags=(row[5],))

    def cancel():
        picked = table.selection()
        if not picked:
            messagebox.showwarning("Select Booking", "Select a booking first.")
            return

        row = rows[int(picked[0])]
        if row[5] == "Cancelled":
            messagebox.showinfo("Already Cancelled", "This booking is already cancelled.")
            return
        if not messagebox.askyesno("Cancel Booking", "Cancel this booking?"):
            return

        try:
            backend.cancel_booking(row[0], current_user)            
        except Exception as error:
            show_error(error, "Cannot Cancel")
            return

        messagebox.showinfo("Success", "Booking cancelled.")
        bookings_page()

    bottom = Frame(page, bg=BG)
    bottom.pack(fill="x", padx=28, pady=(0, 20))
    make_button(bottom, "✖  Cancel Selected Booking", RED, cancel).pack(side="left")



# FIXTURES PAGE
def fixtures_page():
    clear()
    highlight_nav("Fixtures")
    page_header("Sports Fixtures", "View matches, scheduled games, and completed results")

    sports = backend.get_sports()                                   
    filters = Frame(page, bg=BG)
    filters.pack(fill="x", padx=28, pady=(0, 10))

    make_label(filters, "SPORT", F_SMALL, MUTED, BG).pack(side="left", padx=(0, 6))
    sport_filter = make_combo(filters, ["All"] + sports, 12)
    sport_filter.set("All")
    sport_filter.pack(side="left", padx=(0, 14))

    make_label(filters, "STATUS", F_SMALL, MUTED, BG).pack(side="left", padx=(0, 6))
    status_filter = make_combo(filters, ["All", "Scheduled", "Completed"], 11)
    status_filter.set("All")
    status_filter.pack(side="left")

    # ----- the table -----
    frame, table = make_table(
        page, ("ID", "Sport", "Team 1", "Team 2", "Venue", "Date", "Time", "Score", "Status"),
        (45, 100, 140, 140, 150, 110, 170, 90, 100))
    frame.pack(fill="both", expand=True, padx=28, pady=(0, 10))
    table.tag_configure("Scheduled", foreground=BLUE)
    table.tag_configure("Completed", foreground=GREEN)

    def refresh(event=None):
        for item in table.get_children():                          
            table.delete(item)

        try:
            rows = backend.get_fixtures(sport_filter.get(), status_filter.get())   
        except Exception as error:
            show_error(error, "Fixtures Error")
            return

        # each row is (id, sport, team1, team2, venue, date, time, score1, score2, status)
        for row in rows:
            score = "-"
            if row[7] is not None and row[8] is not None:
                score = str(row[7]) + " - " + str(row[8])
            table.insert("", END, iid=str(row[0]),
                         values=(row[0], row[1], row[2], row[3], row[4],
                                 row[5], row[6], score, row[9]),
                         tags=(row[9],))

    sport_filter.bind("<<ComboboxSelected>>", refresh)             
    status_filter.bind("<<ComboboxSelected>>", refresh)

    # ----- only the admin gets the buttons below -----
    if current_user != backend.ADMIN_USER:
        make_label(page, "Only the admin can schedule fixtures and enter results.",
                   F_BODY, MUTED, BG).pack(anchor="w", padx=28, pady=(0, 14))
        refresh()
        return

    controls = Frame(page, bg=BG)
    controls.pack(fill="x", padx=28, pady=(0, 16))

    def selected_id():
        picked = table.selection()
        if not picked:
            messagebox.showwarning("Select Fixture", "Select a fixture from the table first.")
            return None
        return int(picked[0])

    
    def add_fixture_window():
        win = Toplevel(top)
        win.title("Add Sports Fixture")
        win.configure(bg=CARD)
        win.grab_set()

        box = Frame(win, bg=CARD, padx=22, pady=16)
        box.pack()

        make_label(box, "SPORT", F_SMALL, MUTED).pack(anchor="w", pady=(8, 3))
        sport_box = make_combo(box, sports, 30)
        sport_box.set(sports[0])
        sport_box.pack(fill="x")

        make_label(box, "TEAM 1", F_SMALL, MUTED).pack(anchor="w", pady=(8, 3))
        team1_entry = make_entry(box)
        team1_entry.pack(fill="x", ipady=5)

        make_label(box, "TEAM 2", F_SMALL, MUTED).pack(anchor="w", pady=(8, 3))
        team2_entry = make_entry(box)
        team2_entry.pack(fill="x", ipady=5)

        make_label(box, "FACILITY", F_SMALL, MUTED).pack(anchor="w", pady=(8, 3))
        venue_box = make_combo(box, backend.get_facilities(), 30)
        venue_box.pack(fill="x")

        def sport_changed(event=None):
            """When the sport changes, pick that sport's usual ground."""
            venue_box.set(backend.SPORT_FACILITY.get(sport_box.get(), ""))

        sport_box.bind("<<ComboboxSelected>>", sport_changed)
        sport_changed()

        make_label(box, "DATE (YYYY-MM-DD)", F_SMALL, MUTED).pack(anchor="w", pady=(8, 3))
        date_entry = make_entry(box)
        date_entry.insert(0, str(date.today() + timedelta(days=1)))
        date_entry.pack(fill="x", ipady=5)

        make_label(box, "TIME SLOT", F_SMALL, MUTED).pack(anchor="w", pady=(8, 3))
        time_box = make_combo(box, backend.TIME_SLOTS, 30)
        time_box.current(0)
        time_box.pack(fill="x")

        def save_fixture():
            sport = sport_box.get()
            team1 = team1_entry.get().strip()
            team2 = team2_entry.get().strip()
            facility = venue_box.get()
            slot = time_box.get()
            day = read_date(date_entry.get())

            if team1 == "" or team2 == "" or facility == "":
                messagebox.showwarning("Missing Details", "Please complete every field.",
                                       parent=win)
                return
            if day is None:
                messagebox.showwarning("Invalid Date", "Enter the date as YYYY-MM-DD.",
                                       parent=win)
                return
            if day < date.today():
                messagebox.showwarning("Invalid Date", "A new fixture cannot be in the past.",
                                       parent=win)
                return

            try:
                backend.add_fixture(sport, team1, team2, facility, day, slot,
                                    current_user)                   # <-- backend
            except Exception as error:
                show_error(error, "Cannot Add Fixture", parent=win)
                return

            messagebox.showinfo("Success", "Fixture added successfully.", parent=win)
            win.destroy()
            refresh()

        make_button(box, "Save Fixture", GREEN, save_fixture, fg="#052e16").pack(
            anchor="e", pady=(16, 0))

    # ---------- window: enter a result ----------
    def result_window():
        fixture_id = selected_id()
        if fixture_id is None:
            return

        values = table.item(str(fixture_id), "values")      
        team1 = values[2]
        team2 = values[3]
        if values[8] == "Completed":
            messagebox.showinfo("Already Completed", "This fixture already has a result.")
            return

        win = Toplevel(top)
        win.title("Enter Match Result")
        win.configure(bg=CARD)
        win.grab_set()

        box = Frame(win, bg=CARD, padx=24, pady=18)
        box.pack()
        make_label(box, team1 + " vs " + team2, F_BOLD).pack(pady=(0, 14))

        make_label(box, team1 + " score", F_SMALL, MUTED).pack(anchor="w")
        score1_entry = make_entry(box)
        score1_entry.pack(fill="x", ipady=5, pady=(3, 10))

        make_label(box, team2 + " score", F_SMALL, MUTED).pack(anchor="w")
        score2_entry = make_entry(box)
        score2_entry.pack(fill="x", ipady=5, pady=(3, 14))
        score1_entry.focus_set()

        def save_result():
            try:
                score1 = int(score1_entry.get().strip())
                score2 = int(score2_entry.get().strip())
            except ValueError:
                messagebox.showwarning("Invalid Score", "Enter whole-number scores.",
                                       parent=win)
                return

            try:
                backend.save_result(fixture_id, score1, score2)     # <-- backend
            except Exception as error:
                show_error(error, "Invalid Score", parent=win)
                return

            messagebox.showinfo("Success", "Match result saved successfully.", parent=win)
            win.destroy()
            refresh()

        make_button(box, "Save Result", GREEN, save_result, fg="#052e16").pack(anchor="e")

    # ---------- delete a fixture ----------
    def delete_fixture():
        fixture_id = selected_id()
        if fixture_id is None:
            return
        if not messagebox.askyesno("Delete Fixture",
                                   "Are you sure you want to delete this fixture?"):
            return

        try:
            backend.delete_fixture(fixture_id)                      # <-- backend
        except Exception as error:
            show_error(error, "Cannot Delete")
            return

        messagebox.showinfo("Success", "Fixture deleted successfully.")
        refresh()

    make_button(controls, "+ Add Fixture", GREEN, add_fixture_window, fg="#052e16").pack(
        side="left")
    make_button(controls, "Enter Result", BLUE, result_window).pack(side="left", padx=8)
    make_button(controls, "Delete Fixture", RED, delete_fixture).pack(side="left")

    refresh()



# START THE PROGRAM
def close_app():
    backend.close()
    top.destroy()


top.protocol("WM_DELETE_WINDOW", close_app)
login_page()
top.mainloop()
