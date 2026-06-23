import sqlite3
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent.parent


class Database:
    def __init__(self, db_path: str = "data/gym.db"):
        self.db_path = BASE_DIR / db_path
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self._create_tables()

    def _get_connection(self):
        return sqlite3.connect(self.db_path)

    def _create_tables(self):
        query_ui = """
        CREATE TABLE IF NOT EXISTS ui_state (
            message_id INTEGER PRIMARY KEY,
            chat_id INTEGER,
            cycle INTEGER,
            exercise INTEGER,
            set_num INTEGER,
            who TEXT,
            weight REAL,
            reps INTEGER,
            target_date TEXT
        )
        """
        query_logs = """
        CREATE TABLE IF NOT EXISTS workout_logs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
            workout_date TEXT,
            who TEXT,
            cycle INTEGER,
            exercise TEXT,
            set_num INTEGER,
            weight REAL,
            reps INTEGER
        )
        """
        with self._get_connection() as conn:
            conn.execute(query_ui)
            conn.execute(query_logs)
            conn.commit()

    def save_state(self, msg_id: int, chat_id: int, cycle: int, exercise: int, set_num: int = 1, who: str = "me",
                   weight: float = 0.0, reps: int = 15, target_date: str = None):
        query = """
        INSERT INTO ui_state (message_id, chat_id, cycle, exercise, set_num, who, weight, reps, target_date)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        ON CONFLICT(message_id) DO UPDATE SET
            cycle=excluded.cycle, exercise=excluded.exercise, set_num=excluded.set_num,
            who=excluded.who, weight=excluded.weight, reps=excluded.reps, target_date=excluded.target_date
        """
        with self._get_connection() as conn:
            conn.execute(query, (msg_id, chat_id, cycle, exercise, set_num, who, weight, reps, target_date))
            conn.commit()

    def get_state(self, msg_id: int) -> dict:
        query = "SELECT cycle, exercise, set_num, who, weight, reps, target_date FROM ui_state WHERE message_id = ?"
        with self._get_connection() as conn:
            row = conn.execute(query, (msg_id,)).fetchone()
            if row:
                return {
                    "cycle": row[0], "ex": row[1], "set": row[2],
                    "who": row[3], "weight": row[4], "reps": row[5],
                    "target_date": row[6]
                }
            return None

    def save_log(self, date_str: str, who: str, cycle: int, exercise: str, set_num: int, weight: float, reps: int):
        query = """
        INSERT INTO workout_logs (workout_date, who, cycle, exercise, set_num, weight, reps)
        VALUES (?, ?, ?, ?, ?, ?, ?)
        """
        with self._get_connection() as conn:
            conn.execute(query, (date_str, who, cycle, exercise, set_num, weight, reps))
            conn.commit()


db = Database()