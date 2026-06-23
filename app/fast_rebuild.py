import time
from collections import defaultdict
from app.core.config import config
from app.core.database import db
from app.bot.keyboards import EXERCISES
from app.exporters.spreadsheet import GymSpreadsheet
from app.exporters.styles import (
    DATA_FORMAT, DATA_LAST_ROW_FORMAT,
    EXERCISE_FORMAT, EXERCISE_LAST_ROW_FORMAT,
    REPS_FORMAT, DATE_FORMAT
)

def fast_rebuild():
    with db._get_connection() as conn:
        cursor = conn.execute("""
            SELECT workout_date, who, cycle, exercise, set_num, weight, reps 
            FROM workout_logs 
            ORDER BY id ASC
        """)
        logs = cursor.fetchall()

    if not logs:
        return

    # data[who][cycle][date][exercise][set_num] = (weight, reps)
    grouped_data = defaultdict(lambda: defaultdict(lambda: defaultdict(lambda: defaultdict(dict))))
    dates_order = defaultdict(lambda: defaultdict(list))

    for log in logs:
        date_str, who, cycle, exercise, set_num, weight, reps = log
        grouped_data[who][cycle][date_str][exercise][set_num] = (weight, reps)

        if date_str not in dates_order[who][cycle]:
            dates_order[who][cycle].append(date_str)

    for who in ['me', 'friend']:
        if who not in grouped_data:
            continue

        sheet_id = config.SPREADSHEET_ID_ME if who == 'me' else config.SPREADSHEET_ID_FRIEND
        gym_doc = GymSpreadsheet(sheet_id)
        user_name = 'Я' if who == 'me' else 'Друг'

        for cycle in grouped_data[who]:
            print(f"Data in process: {user_name} -> Cycle {cycle}...")

            ws = gym_doc._get_or_create_worksheet(cycle)

            values_to_insert = []
            formats = []
            merge_requests = []

            current_row = 3
            cycle_exercises = EXERCISES[cycle]

            for date_str in dates_order[who][cycle]:
                start_row = current_row

                for idx, ex_name in enumerate(cycle_exercises):
                    row_data = [date_str if idx == 0 else "", ex_name] + [""] * 10

                    if ex_name in grouped_data[who][cycle][date_str]:
                        sets = grouped_data[who][cycle][date_str][ex_name]
                        for set_num, (weight, reps) in sets.items():
                            if 1 <= set_num <= 5:
                                col_w_idx = 2 + (set_num - 1) * 2
                                col_r_idx = 3 + (set_num - 1) * 2
                                row_data[col_w_idx] = weight
                                row_data[col_r_idx] = reps

                    values_to_insert.append(row_data)
                    current_row += 1

                end_row = current_row - 1

                merge_requests.append({
                    "mergeCells": {
                        "range": {
                            "sheetId": ws.id,
                            "startRowIndex": start_row - 1,
                            "endRowIndex": end_row,
                            "startColumnIndex": 1,
                            "endColumnIndex": 2
                        },
                        "mergeType": "MERGE_ALL"
                    }
                })

                formats.append({"range": f"B{start_row}:B{end_row}", "format": DATE_FORMAT})
                formats.append({"range": f"C{end_row}", "format": EXERCISE_LAST_ROW_FORMAT})
                formats.append({"range": f"D{end_row}:M{end_row}", "format": DATA_LAST_ROW_FORMAT})

                if end_row > start_row:
                    formats.append({"range": f"C{start_row}:C{end_row - 1}", "format": EXERCISE_FORMAT})
                    formats.append({"range": f"D{start_row}:M{end_row - 1}", "format": DATA_FORMAT})

                for col in ["E", "G", "I", "K", "M"]:
                    formats.append({"range": f"{col}{start_row}:{col}{end_row}", "format": REPS_FORMAT})

            if values_to_insert:
                ws.update(f"B3:M{current_row - 1}", values_to_insert)
                ws.batch_format(formats)
                if merge_requests:
                    gym_doc.doc.batch_update({"requests": merge_requests})

            time.sleep(2)

if __name__ == "__main__":
    fast_rebuild()