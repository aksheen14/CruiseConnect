#!/usr/bin/env python3
"""Writes seed.sql to stdout. The fixed random seed makes the output reproducible."""
import random
from datetime import datetime, timedelta

rng = random.Random(111)
DURATION = timedelta(minutes=90)
FMT = "%Y-%m-%d %H:%M:%S"


def q(value):
    if value is None:
        return "NULL"
    if isinstance(value, (int, float)):
        return str(value)
    return "'" + str(value).replace("'", "''") + "'"


def insert(table, rows):
    for row in rows:
        print(f"INSERT INTO {table} VALUES ({', '.join(q(v) for v in row)});")


FIRST = """Avery Blake Casey Dana Elliot Finley Gray Harper Indra Jordan Kai Logan Morgan Noor
Oakley Parker Quinn Riley Sage Taylor""".split()
LAST = """Abara Bianchi Castillo Dubois Eriksen Farah Gupta Haddad Ito Jensen Kowalski Lindqvist
Moreno Nakamura Okafor Petrov Quintero Rossi Singh Tran""".split()
names = [f"{first} {last}" for first in FIRST for last in LAST]
rng.shuffle(names)
name_iter = iter(names)

# Staff: staff 15 deliberately manages nothing.
staff_plan = (
    [("Guest Services Officer", "Guest Services")] * 3
    + [("Excursion Officer", "Shore Operations")] * 3
    + [("Dining Officer", "Food and Beverage")] * 3
    + [("Entertainment Officer", "Entertainment")] * 3
    + [("Guest Services Trainee", "Guest Services")] * 3
)
staff = [(i, next(name_iter), role, dept) for i, (role, dept) in enumerate(staff_plan, 1)]

# Cabins: cabin 60 stays empty so a passenger can move there.
cabins = []
for cabin_id in range(1, 61):
    deck = 3 + (cabin_id - 1) // 8
    number = f"{deck}{(cabin_id - 1) % 8 + 1:02d}"
    capacity = 4 if cabin_id == 60 else rng.choice([2, 3, 3, 4])
    cabins.append([cabin_id, number, deck, capacity, 0, rng.randint(1, 3)])

# Passengers: fill the available beds at random.
beds = [c[0] for c in cabins[:-1] for _ in range(c[3])]
rng.shuffle(beds)
assert len(beds) >= 150
passengers = []
for pid in range(1, 151):
    name = next(name_iter)
    domain = rng.choice(["gmail.com", "yahoo.com", "outlook.com", "icloud.com"])
    email = f"{name.lower().replace(' ', '.')}{pid}@{domain}"
    phone = f"209-555-{rng.randint(0, 9999):04d}"
    cabin_id = beds[pid - 1]
    cabins[cabin_id - 1][4] += 1
    passengers.append((pid, name, email, phone, rng.randint(18, 82), cabin_id))

# Excursions: 3 at each port. Excursion 4 is exactly full and 15 is nearly empty.
ports = ["Cozumel", "Nassau", "Roatan", "Grand Cayman", "Belize City"]
activities = ["Snorkeling Reef Tour", "Historic Town Walk", "Jungle Zipline"]
base_date = datetime(2027, 3, 3)
excursions = []
for i in range(15):
    port = ports[i // 3]
    capacity = 8 if i == 3 else (40 if i == 14 else rng.randint(15, 35))
    date = (base_date + timedelta(days=i // 3)).strftime("%Y-%m-%d")
    excursions.append(
        [i + 1, port, f"{port} {activities[i % 3]}", rng.randint(9, 30) * 5 + 0.99, date, capacity, 0, 4 + i % 3]
    )

booking_pairs = {(1, 1), (1, 2), (1, 3), (2, 1), (2, 2), (2, 3)}  # all of Cozumel
for ex in excursions:
    if ex[0] == 4:
        target = 8
    elif ex[0] == 15:
        target = 3
    else:
        target = int(ex[5] * rng.uniform(0.4, 0.9))
    already = {p for p, e in booking_pairs if e == ex[0]}
    # Passengers 140-150 book no excursions.
    for pid in rng.sample([p for p in range(1, 140) if p not in already], target - len(already)):
        booking_pairs.add((pid, ex[0]))
books = []
for pid, ex_id in sorted(booking_pairs):
    excursions[ex_id - 1][6] += 1
    stamp = datetime(2027, 1, 5) + timedelta(hours=rng.randint(0, 24 * 45))
    books.append((pid, ex_id, stamp.strftime(FMT)))

venues = [
    (1, "Main Dining Room", "International", 60, 7),
    (2, "Trattoria Mare", "Italian", 30, 7),
    (3, "Sakura House", "Japanese", 24, 8),
    (4, "Cantina del Sol", "Mexican", 28, 8),
    (5, "Harbor Grill", "Steakhouse", 26, 9),
    (6, "The Chef's Table", "French", 12, 9),
]

# Venue 6 is hand-written: full at 19:00, then free again once the 18:00 party has left.
reservations = [
    (10, 6, "2027-03-02 18:00:00", 6),
    (11, 6, "2027-03-02 19:00:00", 6),
    (12, 6, "2027-03-02 20:30:00", 6),
]


def seats_taken(venue_id, start):
    """Seats held by any reservation overlapping [start, start + 90 minutes)."""
    total = 0
    for _, v, time, party in reservations:
        other = datetime.strptime(time, FMT)
        if v == venue_id and other < start + DURATION and other + DURATION > start:
            total += party
    return total


# Passengers 148-150 have no activity of any kind.
slots = [
    datetime(2027, 3, day, hour, minute)
    for day in range(1, 8)
    for hour in range(17, 21)
    for minute in (0, 30)
]
capacity_of = {v[0]: v[3] for v in venues}
taken = {(p, v, t) for p, v, t, _ in reservations}
while len(reservations) < 110:
    pid, venue_id = rng.randint(1, 135), rng.randint(1, 5)
    start = rng.choice(slots)
    party = rng.randint(1, 6)
    key = (pid, venue_id, start.strftime(FMT))
    if key not in taken and seats_taken(venue_id, start) + party <= capacity_of[venue_id]:
        taken.add(key)
        reservations.append((pid, venue_id, key[2], party))
reservations.sort(key=lambda r: (r[1], r[2], r[0]))

# Events: event 15 has no RSVPs.
event_names = [
    "Broadway Revue", "Comedy Night", "Sunrise Yoga", "Trivia Championship", "Salsa Lesson",
    "Magic Show", "Wine Tasting", "Karaoke Finals", "Art Auction", "Cooking Demo",
    "Stargazing on Deck", "Jazz Lounge Set", "Dance Party", "Captain's Reception", "Origami Workshop",
]
locations = ["Grand Theater", "Lido Deck", "Atrium", "Sky Lounge", "Pool Deck"]
events = []
for i, name in enumerate(event_names):
    time = datetime(2027, 3, 1 + i % 7, 10 + (i * 3) % 12)
    events.append([i + 1, name, rng.choice(locations), time.strftime(FMT), rng.randint(20, 60), 0, 10 + i % 3])

rsvps = []
for ev in events[:-1]:
    # Passengers 148-150 never RSVP.
    for pid in sorted(rng.sample(range(1, 148), int(ev[4] * rng.uniform(0.2, 0.9)))):
        stamp = datetime(2027, 2, 1) + timedelta(hours=rng.randint(0, 24 * 25))
        rsvps.append((pid, ev[0], stamp.strftime(FMT)))
        ev[5] += 1

print("PRAGMA foreign_keys = ON;")
print("BEGIN TRANSACTION;")
insert("Staff", staff)
insert("Cabin", cabins)
insert("Passenger", passengers)
insert("Excursion", excursions)
insert("Dining_Venues", venues)
insert("Event", events)
insert("Books_Excursion", books)
insert("Reserves_Dining", reservations)
insert("RSVPs_Event", rsvps)
print("COMMIT;")
