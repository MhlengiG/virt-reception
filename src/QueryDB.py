# Final complete DBQuery class with all upgrades and enhancements
from datetime import datetime, timedelta, time
import random
import mysql.connector
from rapidfuzz import process

def get_day_index(day_name):
    days = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday']
    return days.index(day_name)

def parse_time_str(time_str):
    return datetime.strptime(time_str, "%H:%M:%S").time()

def normalize_time(val):
    if isinstance(val, time):
        return val
    return parse_time_str(str(val))

class DBQuery:
    def __init__(self, host='UKZNconnection', user='root', password='Dortmund11!.', database='ukzn'):
        self.conn = mysql.connector.connect(
            host=host,
            user=user,
            password=password,
            database=database,
            ssl_disabled = True
        )
        self.cursor = self.conn.cursor(dictionary=True)
        self.conn.ping(reconnect=True, attempts=3, delay=2)
        # self.cursor = self.conn.cursor()

    def ensure_connection(self):
        try:
            self.conn.ping(reconnect=True, attempts=3, delay=2)
        except mysql.connector.Error as e:
            print("DB reconnection triggered:", e)
            self.conn.reconnect(attempts=3, delay=2)
            self.cursor = self.conn.cursor(dictionary=True)

    def get_current_day(self):
        return datetime.now().strftime("%A")

    def fuzzy_match(self, query_value, column, table, min_score=70):
        self.cursor.execute(f"SELECT DISTINCT {column} FROM {table};")
        options = [row[column] for row in self.cursor.fetchall() if row[column]]
        match, score, _ = process.extractOne(query_value.lower(), options)
        print(f"🔍 Fuzzy Match: '{query_value}' → '{match}' [score: {score}]")
        return match if score >= min_score else None

    def query(self, intent, slots):
        print(f"🧠 Query Intent: {intent}")
        print(f"🔍 Extracted Slots: {slots}")

        if intent == "greeting_query":
            return random.choice([
                "Hey there! How can I assist you today?",
                "Hello! What would you like help with?",
                "Hi! Feel free to ask about staff, lectures, or rooms."
            ])
        elif intent == "goodbye_query":
            return random.choice([
                "Goodbye! Have a great day!",
                "See you later! Stay safe!",
                "Catch you next time!"
            ])

        if intent == "staff_availability":
            return self.handle_staff_availability(slots)
        elif intent == "location_of":
            return self.handle_location_of(slots)
        elif intent == "timetable_query":
            return self.handle_timetable_query(slots)

        return "Sorry, I’m not trained to handle that request."

    def handle_staff_availability(self, slots):
        self.ensure_connection()
        if "surname" not in slots:
            return "Please specify the staff member."

        surname = self.fuzzy_match(slots["surname"], "surname", "staff") or slots["surname"]
        self.cursor.execute("SELECT available_today FROM staff WHERE surname = %s", (surname,))
        result = self.cursor.fetchone()
        if result:
            return f"Yes, {surname} is currently available." if result["available_today"] else f"No, {surname} is currently unavailable or in class."
        return f"I couldn't find anyone with the surname {surname}."

    def handle_location_of(self, slots):
        self.ensure_connection()
        # Remove hallucinated surnames like "class", "lesson"
        hallucinated_starts = {"cla", "les", "lec", "less", "lect","and","And"}
        if "surname" in slots:
            s = slots["surname"].lower()
            if len(s) <= 6 and any(s.startswith(h) for h in hallucinated_starts):
                print(f"⚠️ Force dropped surname: {slots['surname']}")
                slots.pop("surname", None)
                slots.pop("person_role", None)

        # 🔧 Normalize class_type
        class_type_map = {
            "lesson?": "lecture", "lesson": "lecture", "lessopn": "lecture",
            "lect": "lecture", "class": "lecture", "lecture?": "lecture",
            "lab": "lab", "prac": "lab", "practical": "lab",
            "tutorial": "tutorial", "tut": "tutorial"
        }
        original_type = slots.get("class_type", "lecture").lower()
        class_type = class_type_map.get(original_type, original_type)

        # 🧑‍🏫 Staff office lookup
        if "surname" in slots:
            surname = self.fuzzy_match(slots["surname"], "surname", "staff") or slots["surname"]
            self.cursor.execute("SELECT office FROM staff WHERE surname = %s", (surname,))
            result = self.cursor.fetchone()
            if result and result["office"]:
                return f"You can find {surname}'s office in room {result['office']}."
            return f"No office details found for {surname}."

        # 🏛 Room type lookup (e.g. toilets, labs, reception)
        if "room_type" in slots:
            room_type_raw = slots["room_type"]
            fuzzy_room_type = self.fuzzy_match(room_type_raw, "room_type", "room_locations") or room_type_raw

            self.cursor.execute("""
                SELECT location FROM room_locations
                WHERE room_type = %s
            """, (fuzzy_room_type,))
            location_result = self.cursor.fetchone()

            if location_result:
                return f"The {fuzzy_room_type.lower()} is {location_result['location']}"
            else:
                return f"Sorry, I couldn’t find a location for the {room_type_raw.lower()}."

        # 📚 Subject-based lookup (e.g. “Where is the Digital Systems lecture?”)
        if "academic_subject" in slots:
            subject = slots["academic_subject"].strip().lower().replace("’s", "").replace("'", "")
            fuzzy_subject = self.fuzzy_match(subject, "academic_subject", "timetable") or subject

            self.cursor.execute("""
                SELECT room_id FROM timetable
                WHERE academic_subject = %s AND class_type = %s LIMIT 1
            """, (fuzzy_subject, class_type))
            result = self.cursor.fetchone()

            if result and result["room_id"]:
                return f"The {class_type} for {fuzzy_subject.title()} is in room {result['room_id']}."

            # Try as a fallback: maybe it's a named room_type instead
            self.cursor.execute("""
                SELECT location FROM room_locations
                WHERE room_type LIKE %s
            """, (f"%{fuzzy_subject}%",))
            alt_result = self.cursor.fetchone()
            if alt_result:
                return f"I couldn’t find a timetable entry, but {fuzzy_subject.title()} may be in {alt_result['location']}."

            return f"I couldn't find the venue for the {class_type} of {fuzzy_subject.title()}."

        # No recognizable information
        return "I need more details to find the location."

    def handle_timetable_query(self, slots):
        self.ensure_connection()
        subject = slots.get("academic_subject", "").replace("’s", "").replace("'", "").strip()

        # 🔧 Normalize class_type inside timetable_query too
        class_type_map = {
            "lesson?": "lecture", "lesson": "lecture", "lect": "lecture",
            "class": "lecture", "tutorial": "tutorial", "lab": "lab", "prac": "lab", "tut": "tutorial",
            "practical": "lab", "class?": "lecture", "class.": "lecture", "lecture.": "lecture", "class": "lecture"
        }
        original_type = slots.get("class_type", "lecture").lower()
        class_type = class_type_map.get(original_type, original_type)

        if not subject:
            return "Please specify the course name."

        subject = self.fuzzy_match(subject, "academic_subject", "timetable") or subject
        self.cursor.execute("""
            SELECT day_of_week, start_time, end_time, room_id 
            FROM timetable 
            WHERE academic_subject = %s AND class_type = %s
        """, (subject, class_type))
        sessions = self.cursor.fetchall()

        if not sessions:
            return f"No sessions found for {subject.title()}."

        now = datetime.now()
        day_map = {day: i for i, day in enumerate(['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday'])}
        future_sessions = []

        # inside handle_timetable_query loop:
        for sess in sessions:
            try:
                day_idx = day_map[sess["day_of_week"]]
                start_time = normalize_time(sess["start_time"])

                next_class_day = (day_idx - now.weekday() + 7) % 7
                next_class_datetime = datetime.combine(
                    now.date() + timedelta(days=next_class_day),
                    start_time
                )

                if next_class_datetime < now:
                    next_class_datetime += timedelta(days=7)

                # Keep times raw in display — no need to parse end_time unless formatting
                future_sessions.append((
                    next_class_datetime,
                    sess["day_of_week"],
                    str(sess["start_time"]),
                    str(sess["end_time"]),
                    sess["room_id"]
                ))

            except Exception as e:
                print("Session parse error:", e)
                continue

        next_class = sorted(future_sessions, key=lambda x: x[0])[0]
        return (
            f"The next {class_type} for {subject.title()} is on {next_class[1]} "
            f"from {next_class[2]} to {next_class[3]} in room {next_class[4]}."
        )

    def close(self):
        self.cursor.close()
        self.conn.close()





