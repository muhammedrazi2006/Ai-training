from collections import deque

# Theater network (graph)
theater_graph = {
    "pvr": ["inox", "cinepolis"],
    "inox": ["pvr", "carnival"],
    "cinepolis": ["pvr"],
    "carnival": ["inox"]
}

# Showtimes (lists)
showtimes = {
    "pvr": ["10:00 AM", "1:00 PM", "6:00 PM"],
    "inox": ["11:00 AM", "3:00 PM", "8:00 PM"],
    "cinepolis": ["9:30 AM", "12:30 PM", "5:30 PM"],
    "carnival": ["10:15 AM", "2:15 PM", "7:15 PM"]
}

# Movies and seat maps (hash maps). Seats are explicit IDs (A1..A5, B1..B5)
def make_seat_map(rows=("A","B"), cols=5):
    return {f"{r}{c}": "available" for r in rows for c in range(1, cols+1)}

theaters = {
    "pvr": {
        "KGF": {"time": "6:00 PM", "seats": make_seat_map()},
        "Pathaan": {"time": "1:00 PM", "seats": make_seat_map()}
    },
    "inox": {
        "Avatar": {"time": "11:00 AM", "seats": make_seat_map()},
        "KGF": {"time": "3:00 PM", "seats": make_seat_map(rows=("A","B","C"))}
    },
    "cinepolis": {
        "RRR": {"time": "5:30 PM", "seats": make_seat_map()},
        "Pathaan": {"time": "12:30 PM", "seats": make_seat_map()}
    },
    "carnival": {
        "KGF": {"time": "2:15 PM", "seats": make_seat_map()},
        "RRR": {"time": "7:15 PM", "seats": make_seat_map(rows=("A","B","C"))}
    }
}

# Ticket rates per theater (optional)
ticket_rates = {"pvr": 250, "inox": 220, "cinepolis": 200, "carnival": 230}

# Combo offers: (name, price, value)
combo_offers = [
    ("Popcorn", 100, 40),
    ("Drink", 60, 20),
    ("Nachos", 120, 50),
    ("Combo Meal", 250, 110)
]

# Booking queue (FCFS)
booking_queue = deque()

# ---------------------------
# Utility helpers
# ---------------------------

def normalize(name: str) -> str:    #its for clean up and standardize user input
    """Normalize input (case/spacing) to lookup keys like 'pvr'."""
    return name.strip().lower().replace(" theater","").replace(" ","_").replace("-","")

def list_theaters():
    return list(theaters.keys())
def list_movies(theater_key):
    return list(theaters[theater_key].keys())

def show_available_seats(theater_key, movie_key):
    seats = theaters[theater_key][movie_key]["seats"]
    available = [s for s, st in seats.items() if st == "available"]
    return available

# BFS to find shortest path in theater network
def find_path_bfs(start, end):
    start = normalize(start)
    end = normalize(end)
    if start not in theater_graph or end not in theater_graph:
        return None
    visited = {start}
    queue = deque([[start]])
    while queue:
        path = queue.popleft()
        node = path[-1]
        if node == end:
            return path
        for neighbor in theater_graph.get(node, []):
            if neighbor not in visited:
                visited.add(neighbor)
                queue.append(path + [neighbor])
    return None


def best_combo_within_budget(budget):
    """Return list of chosen combo item names and total price/value within budget."""
    n = len(combo_offers)
    # dp[i][b] = max value using first i items with budget b
    dp = [[0]*(budget+1) for _ in range(n+1)]
    take = [[False]*(budget+1) for _ in range(n+1)]
    for i in range(1, n+1):
        name, price, value = combo_offers[i-1]
        for b in range(budget+1):
            # don't take
            dp[i][b] = dp[i-1][b]
            # take if possible
            if price <= b:
                val_if_taken = dp[i-1][b-price] + value
                if val_if_taken > dp[i][b]:
                    dp[i][b] = val_if_taken
                    take[i][b] = True
    # reconstruct
    b = budget
    chosen = []
    total_cost = 0
    for i in range(n, 0, -1):
        if take[i][b]:
            name, price, value = combo_offers[i-1]
            chosen.append((name, price))
            total_cost += price
            b -= price
    chosen.reverse()
    return chosen, total_cost

# ---------------------------
# Booking functions
# ---------------------------
def add_booking_request():
    # Choose theater
    print("\nAvailable Theaters:")
    keys = list_theaters()
    for i, t in enumerate(keys, 1):
        print(f"{i}. {t.title()} (Ticket: ₹{ticket_rates.get(t,'N/A')})")
    try:
        ti = int(input("Choose theater number: ").strip())
        theater_key = keys[ti-1]
    except Exception:
        print("Invalid choice.")
        return

    # Choose movie
    movies = list_movies(theater_key)
    print(f"\nMovies at {theater_key.title()}:")
    for i, m in enumerate(movies, 1):
        info = theaters[theater_key][m]
        print(f"{i}. {m} — Time: {info['time']} — Seats left: {len(show_available_seats(theater_key,m))}")
    try:
        mi = int(input("Choose movie number: ").strip())
        movie_key = movies[mi-1]
    except Exception:
        print("Invalid movie choice.")
        return

    # Choose seats (show available)
    available = show_available_seats(theater_key, movie_key)
    print("\nAvailable seats:", ", ".join(available))
    seat_input = input("Enter seat codes to book (comma separated, e.g. A1,A2): ").strip().upper()
    selected = [s.strip() for s in seat_input.split(",") if s.strip()]

    # Validate seats are available
    invalid = [s for s in selected if s not in available]
    if invalid:
        print("These seats are not available or invalid:", ", ".join(invalid))
        return

    name = input("Enter your name: ").strip()
    # append booking request to queue
    booking_queue.append((name, theater_key, movie_key, selected))
    print(f"📩 Booking request added for {name}: {movie_key} at {theater_key}, seats: {selected}")

def process_next_booking():
    if not booking_queue:
        print("No booking requests in queue.")
        return
    name, theater_key, movie_key, seats = booking_queue.popleft()
    # verify seats still available
    available = show_available_seats(theater_key, movie_key)
    invalid = [s for s in seats if s not in available]
    if invalid:
        print(f"❌ Cannot fulfill booking for {name}. Seats unavailable: {invalid}")
        return
    # mark seats booked
    for s in seats:
        theaters[theater_key][movie_key]["seats"][s] = "booked"
    price = ticket_rates.get(theater_key, 0) * len(seats)
    print(f"✅ Booking confirmed for {name}: {movie_key} at {theater_key} | Seats: {seats} | Ticket total: ₹{price}")

    # suggest combo
    want = input("Do you want a combo suggestion for your budget? (y/n): ").strip().lower()
    if want == "y":
        try:
            budget = int(input("Enter combo budget (₹): ").strip())
        except:
            print("Invalid budget.")
            return
        chosen, total_cost = best_combo_within_budget(budget)
        if chosen:
            print("💡 Best combo within budget:")
            for name_p, price_p in chosen:
                print(f"- {name_p} (₹{price_p})")
            print(f"Total combo cost: ₹{total_cost}")
        else:
            print("No combo fits the budget.")

def view_showtimes_and_movies():
    print("\nTheaters and showtimes:")
    for t, movie_map in theaters.items():
        print(f"\n{t.title()} (Ticket: ₹{ticket_rates.get(t)} ) — Showtimes: {', '.join(showtimes.get(t,[]))}")
        for m, info in movie_map.items():
            seats_left = len(show_available_seats(t, m))
            print(f"  - {m} | Time: {info['time']} | Seats left: {seats_left}")

def view_theater_seats():
    # choose theater and movie to view seats
    keys = list_theaters()
    for i, t in enumerate(keys, 1):
        print(f"{i}. {t.title()}")
    try:
        ti = int(input("Choose theater number: ").strip())
        theater_key = keys[ti-1]
    except:
        print("Invalid choice.")
        return
    movies = list_movies(theater_key)
    for i, m in enumerate(movies, 1):
        print(f"{i}. {m}")
    try:
        mi = int(input("Choose movie number: ").strip())
        movie_key = movies[mi-1]
    except:
        print("Invalid choice.")
        return
    seats = theaters[theater_key][movie_key]["seats"]
    for s, st in seats.items():
        print(f"{s}: {st}")

def find_nearby_menu():
    name = input("Enter your theater name: ").strip()
    path = find_path_bfs(name, name)  # just validate exists
    # normalize input to key
    key = normalize(name)
    if key not in theater_graph:
        print("Theater not recognized.")
        return
    print("Nearby theaters:", ", ".join(theater_graph.get(key, [])))

# ---------------------------
# Main interactive menu
# ---------------------------
def main():
    print("🎬 MOVIE TICKET BOOKING & RECOMMENDATION (in-memory) 🎬")
    while True:
        print("\nMenu:")
        print("1. Add booking request (select theater/movie/time & seats)")
        print("2. Process next booking (from queue)")
        print("3. View theaters, movies & showtimes")
        print("4. View available seats for a movie")
        print("5. Find nearby theaters (graph)")
        print("6. Best combo offer (enter budget)")
        print("7. Exit")
        choice = input("Enter choice: ").strip()
        if choice == "1":
            add_booking_request()
        elif choice == "2":
            process_next_booking()
        elif choice == "3":
            view_showtimes_and_movies()
        elif choice == "4":
            view_theater_seats()
        elif choice == "5":
            find_nearby_menu()
        elif choice == "6":
            try:
                budget = int(input("Enter your budget (₹): ").strip())
            except:
                print("Invalid budget.")
                continue
            chosen, total_cost = best_combo_within_budget(budget)
            if chosen:
                print("Recommended combo items:")
                for name_p, price_p in chosen:
                    print(f"- {name_p} (₹{price_p})")
                print(f"Total cost: ₹{total_cost}")
            else:
                print("No combo fits your budget.")
        elif choice == "7":
            print("Goodbye!")
            break
        else:
            print("Invalid choice — try again.")

if __name__ == "__main__":
    main()
