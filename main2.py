from tkinter import *
from tkinter import messagebox
from datetime import datetime, date, timedelta
import mysql.connector

# ---------- Your MySQL password (do not share this file!) ----------
MYSQL_PASSWORD = "@avishkargite2007"

TIME_SLOTS = ["8:00 AM - 9:00 AM", "10:00 AM - 11:00 AM",
              "4:00 PM - 5:00 PM", "6:00 PM - 7:00 PM"]

# ---------- Step 1: connect to the database ----------
try:
    db = mysql.connector.connect(
        host="localhost",
        user="root",
        password="@avishkargite2007",
        database="campus_sports"
    )
    cursor = db.cursor(buffered=True)
except mysql.connector.Error as error:
    print("Could not connect to MySQL:", error)
    input("Press Enter to close...")
    exit()

# This remembers who is logged in
current_user = ""

# ---------- Step 2: create the main window ----------
top = Tk()
top.title("Campus Sports Booking")
top.geometry("700x520")

# The window has two frames:
#   menu = the buttons at the top (hidden until login)
#   page = the part that changes for every screen
menu = Frame(top)
page = Frame(top)
menu.grid(row=0, column=0)
page.grid(row=1, column=0)
menu.grid_remove()          # hide the menu for now


def clear():
    """Remove everything from the page frame."""
    for widget in page.winfo_children():
        widget.destroy()


# =====================================================
# LOGIN PAGE
# =====================================================
def login_page():
    clear()
    menu.grid_remove()      # hide the menu buttons

    Label(page, text="Campus Sports Booking", font=("Arial", 18, "bold"),
          fg="blue").grid(row=0, column=0, columnspan=2, pady=30)

    Label(page, text="Username").grid(row=1, column=0, pady=5, padx=5)
    user_entry = Entry(page, width=25)
    user_entry.grid(row=1, column=1)

    Label(page, text="Password").grid(row=2, column=0, pady=5, padx=5)
    pass_entry = Entry(page, width=25, show="*")
    pass_entry.grid(row=2, column=1)

    def login():
        global current_user

        username = user_entry.get().strip()
        password = pass_entry.get().strip()

        if username == "" or password == "":
            messagebox.showwarning("Warning", "Enter username and password.")
            return

        # Passwords are saved hashed (SHA2), so we hash what the user
        # typed and compare the two hashes.
        cursor.execute(
            "SELECT username FROM users WHERE username = %s AND password = SHA2(%s, 256)",
            (username, password)
        )
        result = cursor.fetchone()

        if result:
            current_user = result[0]
            menu.grid()             # show the menu buttons
            dashboard_page()
        else:
            messagebox.showerror("Login Failed", "Wrong username or password.")

    Button(page, text="Login", width=15, bg="blue", fg="white",
           command=login).grid(row=3, column=1, pady=20)


# =====================================================
# MENU BUTTONS (created once, shown after login)
# =====================================================
def logout():
    global current_user
    current_user = ""
    login_page()


Button(menu, text="Dashboard", width=14,
       command=lambda: dashboard_page()).grid(row=0, column=0, padx=5, pady=10)
Button(menu, text="Book Facility", width=14,
       command=lambda: booking_page()).grid(row=0, column=1, padx=5)
Button(menu, text="My Bookings", width=14,
       command=lambda: bookings_page()).grid(row=0, column=2, padx=5)
Button(menu, text="Logout", width=10, bg="red", fg="white",
       command=logout).grid(row=0, column=3, padx=5)


# =====================================================
# DASHBOARD PAGE
# =====================================================
def dashboard_page():
    clear()

    # Count only bookings that are still confirmed
    cursor.execute(
        "SELECT COUNT(*) FROM bookings WHERE username = %s AND status = 'Confirmed'",
        (current_user,)
    )
    total = cursor.fetchone()[0]

    Label(page, text="Welcome, " + current_user + "!",
          font=("Arial", 16, "bold")).grid(row=0, column=0, pady=20)
    Label(page, text="Your active bookings: " + str(total),
          font=("Arial", 12), fg="green").grid(row=1, column=0)


# =====================================================
# BOOKING PAGE
# =====================================================
def booking_page():
    clear()

    Label(page, text="Book a Facility",
          font=("Arial", 16, "bold")).grid(row=0, column=0, columnspan=2, pady=10)

    # Facility list - the names come from the database
    Label(page, text="Select Facility").grid(row=1, column=0)
    facility_box = Listbox(page, height=6, width=22, exportselection=0)
    cursor.execute("SELECT facility_name FROM facilities")
    for row in cursor.fetchall():
        facility_box.insert(END, row[0])
    facility_box.grid(row=2, column=0, padx=10)

    # Time slot list
    Label(page, text="Select Time Slot").grid(row=1, column=1)
    time_box = Listbox(page, height=6, width=22, exportselection=0)
    for slot in TIME_SLOTS:
        time_box.insert(END, slot)
    time_box.grid(row=2, column=1, padx=10)

    # Date (starts with tomorrow's date)
    Label(page, text="Date (YYYY-MM-DD)").grid(row=3, column=0, pady=10)
    date_entry = Entry(page, width=25)
    date_entry.insert(0, str(date.today() + timedelta(days=1)))
    date_entry.grid(row=3, column=1)

    # Purpose
    Label(page, text="Purpose").grid(row=4, column=0)
    purpose_entry = Entry(page, width=25)
    purpose_entry.grid(row=4, column=1)

    def save():
        # Check 1: something must be selected in both lists
        if len(facility_box.curselection()) == 0 or len(time_box.curselection()) == 0:
            messagebox.showwarning("Warning", "Select a facility and a time slot.")
            return

        facility = facility_box.get(facility_box.curselection()[0])
        time_slot = time_box.get(time_box.curselection()[0])
        purpose = purpose_entry.get().strip()

        # Check 2: the date must be written correctly
        try:
            booking_date = datetime.strptime(date_entry.get().strip(), "%Y-%m-%d").date()
        except ValueError:
            messagebox.showwarning("Wrong Date", "Write the date like this: 2026-10-15")
            return

        # Check 3: the date must not be in the past
        if booking_date < date.today():
            messagebox.showwarning("Wrong Date", "You cannot book a past date.")
            return

        # Check 4: purpose must not be empty
        if purpose == "":
            messagebox.showwarning("Warning", "Please enter a purpose.")
            return

        # Check 5: is this slot already booked by someone?
        cursor.execute(
            "SELECT COUNT(*) FROM bookings WHERE facility_name = %s "
            "AND booking_date = %s AND time_slot = %s AND status = 'Confirmed'",
            (facility, booking_date, time_slot)
        )
        if cursor.fetchone()[0] > 0:
            messagebox.showwarning("Slot Taken", "That slot is already booked.")
            return

        # Everything is fine - save the booking
        cursor.execute(
            "INSERT INTO bookings (username, facility_name, booking_date, time_slot, purpose) "
            "VALUES (%s, %s, %s, %s, %s)",
            (current_user, facility, booking_date, time_slot, purpose)
        )
        db.commit()

        messagebox.showinfo("Success", "Booking saved!")
        bookings_page()

    Button(page, text="Confirm Booking", bg="green", fg="white",
           command=save).grid(row=5, column=0, columnspan=2, pady=20)


# =====================================================
# MY BOOKINGS PAGE
# =====================================================
def bookings_page():
    clear()

    Label(page, text="My Bookings",
          font=("Arial", 16, "bold")).grid(row=0, column=0, pady=10)

    # Get this user's bookings from the database
    cursor.execute(
        "SELECT booking_id, facility_name, DATE_FORMAT(booking_date, '%d %b %Y'), "
        "time_slot, purpose, status FROM bookings "
        "WHERE username = %s ORDER BY booking_date DESC",
        (current_user,)
    )
    rows = cursor.fetchall()

    # Show each booking as one line in the Listbox
    box = Listbox(page, height=12, width=80)
    for row in rows:
        line = row[1] + " | " + row[2] + " | " + row[3] + " | " + row[4] + " | " + row[5]
        box.insert(END, line)
    box.grid(row=1, column=0, padx=10)

    def cancel():
        if len(box.curselection()) == 0:
            messagebox.showwarning("Warning", "Click on a booking first.")
            return

        row = rows[box.curselection()[0]]    # the selected booking
        booking_id = row[0]
        status = row[5]

        if status == "Cancelled":
            messagebox.showinfo("Info", "This booking is already cancelled.")
            return

        cursor.execute(
            "UPDATE bookings SET status = 'Cancelled' "
            "WHERE booking_id = %s AND username = %s",
            (booking_id, current_user)
        )
        db.commit()

        messagebox.showinfo("Done", "Booking cancelled.")
        bookings_page()

    Button(page, text="Cancel Selected Booking", bg="red", fg="white",
           command=cancel).grid(row=2, column=0, pady=15)


# =====================================================
# START THE PROGRAM
# =====================================================
login_page()
top.mainloop()

# Close the database after the window is closed
cursor.close()
db.close()
