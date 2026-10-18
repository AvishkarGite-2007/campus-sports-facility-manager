# =====================================================
# BACKEND - MySQL Database Connector (with numpy)
# =====================================================

import mysql.connector
import numpy as np

MYSQL_PASSWORD = "@avishkargite2007"  # <-- Update with your MySQL password

ADMIN_USER = "admin"

TIME_SLOTS = [
    "8:00 AM - 9:00 AM", 
    "10:00 AM - 11:00 AM",
    "4:00 PM - 5:00 PM", 
    "6:00 PM - 7:00 PM"
]

SPORT_FACILITY = {
    "Football": "Football Ground",
    "Cricket": "Cricket Ground",
    "Basketball": "Basketball Court",
}

db = None
cursor = None

def connect():
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
    if cursor:
        cursor.close()
    if db:
        db.close()

def check_login(username, password):
    cursor.execute(
        "SELECT username FROM users WHERE username = %s AND password = SHA2(%s, 256)",
        (username, password)
    )
    result = cursor.fetchone()
    return result[0] if result else None

def get_facilities():
    cursor.execute("SELECT facility_name FROM facilities ORDER BY id")
    return [row[0] for row in cursor.fetchall()]

def get_facility_usage():
    cursor.execute(
        "SELECT f.facility_name, "
        "(SELECT COUNT(*) FROM bookings b "
        "  WHERE b.facility_name = f.facility_name AND b.status = 'Confirmed') + "
        "(SELECT COUNT(*) FROM fixtures x WHERE x.facility_name = f.facility_name) "
        "FROM facilities f ORDER BY f.id"
    )
    return [(row[0], int(row[1])) for row in cursor.fetchall()]

def get_booking_summary(username):
    cursor.execute(
        "SELECT COALESCE(SUM(status = 'Confirmed'), 0), "
        "COALESCE(SUM(status = 'Cancelled'), 0) "
        "FROM bookings WHERE username = %s",
        (username,)
    )
    confirmed, cancelled = cursor.fetchone()
    return int(confirmed), int(cancelled)

def get_bookings(username):
    cursor.execute(
        "SELECT booking_id, facility_name, DATE_FORMAT(booking_date, '%d %b %Y'), "
        "time_slot, purpose, status FROM bookings "
        "WHERE username = %s ORDER BY booking_date DESC, booking_id DESC",
        (username,)
    )
    return cursor.fetchall()

def is_slot_taken(facility, booking_date, time_slot):
    cursor.execute(
        "SELECT COUNT(*) FROM bookings WHERE facility_name = %s "
        "AND booking_date = %s AND time_slot = %s AND status = 'Confirmed'",
        (facility, booking_date, time_slot)
    )
    if cursor.fetchone()[0] > 0:
        return True

    cursor.execute(
        "SELECT COUNT(*) FROM fixtures WHERE facility_name = %s "
        "AND fixture_date = %s AND time_slot = %s AND status = 'Scheduled'",
        (facility, booking_date, time_slot)
    )
    return cursor.fetchone()[0] > 0

def add_booking(username, facility, booking_date, time_slot, purpose):
    cursor.execute(
        "INSERT INTO bookings (username, facility_name, booking_date, time_slot, purpose) "
        "VALUES (%s, %s, %s, %s, %s)",
        (username, facility, booking_date, time_slot, purpose)
    )
    db.commit()

def cancel_booking(booking_id, username):
    cursor.execute(
        "UPDATE bookings SET status = 'Cancelled' "
        "WHERE booking_id = %s AND username = %s",
        (booking_id, username)
    )
    db.commit()

def get_sports():
    cursor.execute("SELECT DISTINCT sport FROM teams ORDER BY sport")
    return [row[0] for row in cursor.fetchall()]

def get_teams(sport):
    cursor.execute("SELECT team_name FROM teams WHERE sport = %s ORDER BY team_name", (sport,))
    return [row[0] for row in cursor.fetchall()]

def get_fixtures(sport="All", status="All"):
    sql = ("SELECT fixture_id, sport, team1, team2, facility_name, "
           "DATE_FORMAT(fixture_date, '%d %b %Y'), time_slot, "
           "team1_score, team2_score, status FROM fixtures WHERE 1 = 1")
    values = []
    if sport != "All":
        sql += " AND sport = %s"
        values.append(sport)
    if status != "All":
        sql += " AND status = %s"
        values.append(status)
    sql += " ORDER BY (status = 'Completed'), fixture_date, fixture_id"

    cursor.execute(sql, tuple(values))
    return cursor.fetchall()

def get_upcoming_fixture_count():
    cursor.execute(
        "SELECT COUNT(*) FROM fixtures WHERE status = 'Scheduled' AND fixture_date >= CURDATE()"
    )
    return cursor.fetchone()[0]

def get_next_fixture():
    cursor.execute(
        "SELECT team1, team2, DATE_FORMAT(fixture_date, '%d %b %Y'), time_slot "
        "FROM fixtures WHERE status = 'Scheduled' AND fixture_date >= CURDATE() "
        "ORDER BY fixture_date, fixture_id LIMIT 1"
    )
    return cursor.fetchone()

def add_fixture(sport, team1, team2, facility, fixture_date, time_slot):
    cursor.execute(
        "INSERT INTO fixtures (sport, team1, team2, facility_name, fixture_date, time_slot) "
        "VALUES (%s, %s, %s, %s, %s, %s)",
        (sport, team1, team2, facility, fixture_date, time_slot)
    )
    db.commit()

def save_result(fixture_id, score1, score2):
    cursor.execute(
        "UPDATE fixtures SET team1_score = %s, team2_score = %s, status = 'Completed' "
        "WHERE fixture_id = %s",
        (score1, score2, fixture_id)
    )
    db.commit()

def delete_fixture(fixture_id):
    cursor.execute("DELETE FROM fixtures WHERE fixture_id = %s", (fixture_id,))
    db.commit()

def get_standings(sport):
    teams = get_teams(sport)
    cursor.execute(
        "SELECT team1, team2, team1_score, team2_score FROM fixtures "
        "WHERE sport = %s AND status = 'Completed'",
        (sport,)
    )
    return calculate_standings(teams, cursor.fetchall())

def calculate_standings(teams, results):
    count = len(teams)
    position_of = {name: i for i, name in enumerate(teams)}

    played = np.zeros(count, dtype=int)
    won = np.zeros(count, dtype=int)
    drawn = np.zeros(count, dtype=int)
    lost = np.zeros(count, dtype=int)
    scored = np.zeros(count, dtype=int)
    conceded = np.zeros(count, dtype=int)

    for team1, team2, score1, score2 in results:
        if team1 not in position_of or team2 not in position_of:
            continue
        a = position_of[team1]
        b = position_of[team2]

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