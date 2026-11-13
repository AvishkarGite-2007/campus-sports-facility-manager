import mysql.connector
import numpy as np
MYSQL_PASSWORD = "@avishkargite2007"     
ADMIN_USER = "admin"                     
TIME_SLOTS = [
    "8:00 AM - 9:00 AM",
    "9:00 AM - 10:00 AM",
    "10:00 AM - 11:00 AM",
    "11:00 AM - 12:00 PM",
    "2:00 PM - 3:00 PM",
    "3:00 PM - 4:00 PM",
    "4:00 PM - 5:00 PM",
    "5:00 PM - 6:00 PM",
    "6:00 PM - 7:00 PM"
]

SPORT_FACILITY = {
    "Football": "Football Ground",
    "Cricket": "Cricket Ground",
    "Basketball": "Basketball Court",
    "Badminton": "Badminton Court",
    "Volleyball": "Volleyball Court",
    "Table Tennis": "Table Tennis"
}


IS_FIXTURE = "team1 IS NOT NULL AND team2 IS NOT NULL"

db = None
cursor = None



def connect():
    """Connect to MySQL. Returns True if it worked, otherwise the error text."""
    global db, cursor
    try:
        db = mysql.connector.connect(
            host="localhost",
            user="root",
            password="@avishkargite2007",
            database="campus_sports"
        )
        cursor = db.cursor(buffered=True)
        return True
    except mysql.connector.Error as error:
        return str(error)


def close():
    """Close the database connection."""
    global db, cursor
    if cursor:
        cursor.close()
        cursor = None
    if db and db.is_connected():
        db.close()
        db = None


# USERS
def check_login(username, password):
    """Returns the username if the login is correct, otherwise None.
    Passwords are stored hashed (SHA2), so the typed password is hashed too."""
    cursor.execute(
        "SELECT username FROM users WHERE username = %s AND password = SHA2(%s, 256)",
        (username, password)
    )
    result = cursor.fetchone()
    return result[0] if result else None


# FACILITIES
def get_facilities():
    """Facility names, in the same order as the facilities table."""
    cursor.execute("SELECT facility_name FROM facilities ORDER BY id")
    return [row[0] for row in cursor.fetchall()]


def get_facility_usage():
    """For the dashboard chart: [(facility_name, number of Confirmed bookings), ...]
    (match fixtures are bookings too, so they are counted)."""
    cursor.execute(
        "SELECT f.facility_name, COUNT(b.booking_id) "
        "FROM facilities f "
        "LEFT JOIN bookings b ON b.facility_name = f.facility_name "
        "AND b.status = 'Confirmed' "
        "GROUP BY f.id, f.facility_name ORDER BY f.id"
    )
    return [(row[0], int(row[1])) for row in cursor.fetchall()]


# BOOKINGS
def count_active_bookings(username):
    """How many Confirmed bookings this user has."""
    cursor.execute(
        "SELECT COUNT(*) FROM bookings WHERE username = %s AND status = 'Confirmed'",
        (username,)
    )
    return int(cursor.fetchone()[0])


def get_booking_summary(username):
    """Returns (confirmed, cancelled) booking counts for this user."""
    cursor.execute(
        "SELECT COALESCE(SUM(status = 'Confirmed'), 0), "
        "COALESCE(SUM(status = 'Cancelled'), 0) "
        "FROM bookings WHERE username = %s",
        (username,)
    )
    confirmed, cancelled = cursor.fetchone()
    return int(confirmed), int(cancelled)


def get_bookings(username):
    """All bookings of this user, newest first, as tuples:
    (booking_id, facility_name, date, time_slot, purpose, status)"""
    cursor.execute(
        "SELECT booking_id, facility_name, DATE_FORMAT(booking_date, '%d %b %Y'), "
        "time_slot, purpose, status FROM bookings "
        "WHERE username = %s ORDER BY booking_date DESC, booking_id DESC",
        (username,)
    )
    return cursor.fetchall()


def get_taken_slots(facility, booking_date):
    """The time slots of this facility that are already used on this date
    (by a booking OR by a match fixture). Cancelled bookings do not count."""
    cursor.execute(
        "SELECT DISTINCT time_slot FROM bookings "
        "WHERE facility_name = %s AND booking_date = %s AND status <> 'Cancelled'",
        (facility, booking_date)
    )
    return [row[0] for row in cursor.fetchall()]


def is_slot_taken(facility, booking_date, time_slot):
    """True if the facility is already used in that slot."""
    cursor.execute(
        "SELECT COUNT(*) FROM bookings WHERE facility_name = %s "
        "AND booking_date = %s AND time_slot = %s AND status <> 'Cancelled'",
        (facility, booking_date, time_slot)
    )
    return cursor.fetchone()[0] > 0


def add_booking(username, facility, booking_date, time_slot, purpose):
    """Save a normal (practice) booking. Raises ValueError if it cannot be saved."""
    purpose = purpose.strip()
    if not purpose:
        raise ValueError("Enter the purpose of the booking.")
    if is_slot_taken(facility, booking_date, time_slot):
        raise ValueError("This facility and time slot is already booked.")

    cursor.execute(
        "INSERT INTO bookings "
        "(username, facility_name, booking_date, time_slot, purpose, status) "
        "VALUES (%s, %s, %s, %s, %s, 'Confirmed')",
        (username, facility, booking_date, time_slot, purpose)
    )
    db.commit()


def cancel_booking(booking_id, username):
    """Mark one of the user's bookings as Cancelled. Raises ValueError if it cannot be.
    Team fixtures are not cancelled here - the admin deletes them on the Fixtures page."""
    cursor.execute(
        "SELECT team1, team2, status FROM bookings "
        "WHERE booking_id = %s AND username = %s",
        (booking_id, username)
    )
    row = cursor.fetchone()

    if row is None:
        raise ValueError("Booking not found.")
    if row[0] is not None and row[1] is not None:
        raise ValueError("This is a match fixture. Ask the admin to remove it "
                         "from the Fixtures page.")
    if row[2] == "Cancelled":
        raise ValueError("This booking is already cancelled.")

    cursor.execute(
        "UPDATE bookings SET status = 'Cancelled' "
        "WHERE booking_id = %s AND username = %s",
        (booking_id, username)
    )
    db.commit()



# SPORTS AND TEAMS
def get_sports():
    """The sports the app supports (same order as SPORT_FACILITY)."""
    return list(SPORT_FACILITY.keys())


def get_teams(sport):
    """Team names already used in fixtures of this sport (for the suggestion lists)."""
    cursor.execute(
        "SELECT team1 AS team_name FROM bookings "
        "WHERE sport = %s AND team1 IS NOT NULL AND status <> 'Cancelled' "
        "UNION "
        "SELECT team2 AS team_name FROM bookings "
        "WHERE sport = %s AND team2 IS NOT NULL AND status <> 'Cancelled' "
        "ORDER BY team_name",
        (sport, sport)
    )
    return [row[0] for row in cursor.fetchall()]


def _same_team_spelling(sport, name):
    """If the team already exists (any upper/lower case), reuse its spelling,
    so 'cse warriors' and 'CSE Warriors' are treated as one team."""
    for existing in get_teams(sport):
        if existing.casefold() == name.casefold():
            return existing
    return name



# FIXTURES (rows of the bookings table that have two teams)
def get_fixtures(sport="All", status="All"):
    """Fixtures as tuples:
    (booking_id, sport, team1, team2, facility, date, time_slot,
     team1_score, team2_score, fixture_status)
    Scheduled matches come first, then completed ones."""
    sql = (
        "SELECT booking_id, sport, team1, team2, facility_name, "
        "DATE_FORMAT(fixture_date, '%d %b %Y'), time_slot, "
        "team1_score, team2_score, fixture_status "
        "FROM bookings WHERE " + IS_FIXTURE + " AND status <> 'Cancelled'"
    )
    values = []
    if sport != "All":
        sql += " AND sport = %s"
        values.append(sport)
    if status != "All":
        sql += " AND fixture_status = %s"
        values.append(status)
    sql += " ORDER BY (fixture_status = 'Completed'), fixture_date, booking_id"

    cursor.execute(sql, tuple(values))
    return cursor.fetchall()


def get_upcoming_fixture_count():
    """How many Scheduled fixtures are today or later."""
    cursor.execute(
        "SELECT COUNT(*) FROM bookings WHERE " + IS_FIXTURE + " "
        "AND fixture_status = 'Scheduled' AND fixture_date >= CURDATE() "
        "AND status <> 'Cancelled'"
    )
    return int(cursor.fetchone()[0])


def get_next_fixture():
    """The next Scheduled fixture as (team1, team2, date, time_slot), or None."""
    cursor.execute(
        "SELECT team1, team2, DATE_FORMAT(fixture_date, '%d %b %Y'), time_slot "
        "FROM bookings WHERE " + IS_FIXTURE + " "
        "AND fixture_status = 'Scheduled' AND fixture_date >= CURDATE() "
        "AND status <> 'Cancelled' "
        "ORDER BY fixture_date, booking_id LIMIT 1"
    )
    return cursor.fetchone()


def add_fixture(sport, team1, team2, facility, fixture_date, time_slot,
                username=ADMIN_USER):
    """Schedule a match. It is saved as a Confirmed booking with the match columns filled.
    Raises ValueError if something is wrong."""
    sport = sport.strip()
    team1 = team1.strip()
    team2 = team2.strip()

    if not sport or not team1 or not team2:
        raise ValueError("Enter the sport and both team names.")
    if team1.casefold() == team2.casefold():
        raise ValueError("Team 1 and Team 2 must be different.")
    if is_slot_taken(facility, fixture_date, time_slot):
        raise ValueError("This facility and time slot is already booked.")

    team1 = _same_team_spelling(sport, team1)
    team2 = _same_team_spelling(sport, team2)

    cursor.execute(
        "INSERT INTO bookings "
        "(username, facility_name, booking_date, time_slot, purpose, "
        " sport, team1, team2, fixture_date, fixture_status, status) "
        "VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, 'Scheduled', 'Confirmed')",
        (username, facility, fixture_date, time_slot, sport + " Match",
         sport, team1, team2, fixture_date)
    )
    db.commit()


def save_result(fixture_id, score1, score2):
    """Store the final score and mark the fixture Completed.
    Raises ValueError if the scores are wrong or the fixture cannot take a result."""
    score1 = int(score1)
    score2 = int(score2)
    if score1 < 0 or score2 < 0:
        raise ValueError("Scores cannot be negative.")

    cursor.execute(
        "UPDATE bookings SET team1_score = %s, team2_score = %s, "
        "fixture_status = 'Completed' "
        "WHERE booking_id = %s AND " + IS_FIXTURE + " "
        "AND fixture_status = 'Scheduled' AND status <> 'Cancelled'",
        (score1, score2, fixture_id)
    )
    changed = cursor.rowcount
    db.commit()

    if changed == 0:
        raise ValueError("This fixture was not found or already has a result.")


def delete_fixture(fixture_id):
    """Remove a fixture (only rows that are match fixtures can be removed here)."""
    cursor.execute(
        "DELETE FROM bookings WHERE booking_id = %s AND " + IS_FIXTURE,
        (fixture_id,)
    )
    changed = cursor.rowcount
    db.commit()

    if changed == 0:
        raise ValueError("Fixture not found.")





def calculate_standings(teams, results):
    """teams   = list of team names
    results = list of (team1, team2, score1, score2) for finished matches

    Win = 3 points, draw = 1 point, loss = 0.
    Returns rows: (position, team, played, won, drawn, lost, for, against, diff, points)
    numpy keeps one array per column, with one slot per team."""
    count = len(teams)
    slot_of = {name.casefold(): i for i, name in enumerate(teams)}

    played = np.zeros(count, dtype=int)
    won = np.zeros(count, dtype=int)
    drawn = np.zeros(count, dtype=int)
    lost = np.zeros(count, dtype=int)
    scored = np.zeros(count, dtype=int)
    conceded = np.zeros(count, dtype=int)

    for team1, team2, score1, score2 in results:
        a = slot_of.get(team1.casefold())
        b = slot_of.get(team2.casefold())
        if a is None or b is None or score1 is None or score2 is None:
            continue

        played[a] += 1
        played[b] += 1
        scored[a] += score1
        conceded[a] += score2
        scored[b] += score2
        conceded[b] += score1

        if score1 > score2:
            won[a] += 1
            lost[b] += 1
        elif score1 < score2:
            won[b] += 1
            lost[a] += 1
        else:
            drawn[a] += 1
            drawn[b] += 1

    difference = scored - conceded
    points = won * 3 + drawn

    order = np.lexsort((-scored, -difference, -points))

    rows = []
    for place, i in enumerate(order, start=1):
        rows.append((place, teams[i], int(played[i]), int(won[i]), int(drawn[i]),
                     int(lost[i]), int(scored[i]), int(conceded[i]),
                     int(difference[i]), int(points[i])))
    return rows
