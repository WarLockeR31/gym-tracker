import gspread
from gspread.utils import rowcol_to_a1

from app.core.config import config
from app.core.logger import logger
from app.exporters.google_auth import get_google_client
from app.bot.keyboards import EXERCISES
from app.exporters.styles import (
    HEADER_FORMAT, DATA_FORMAT, DATA_LAST_ROW_FORMAT,
    EXERCISE_FORMAT, EXERCISE_LAST_ROW_FORMAT,
    REPS_FORMAT, DATE_FORMAT
)

_g_client = None


def _get_client() -> gspread.Client:
    global _g_client
    if not _g_client:
        _g_client = get_google_client()
    return _g_client


class GymSpreadsheet:
    def __init__(self, spreadsheet_id: str):
        self.client = _get_client()
        self.spreadsheet_id = spreadsheet_id
        try:
            self.doc = self.client.open_by_key(self.spreadsheet_id)
        except Exception as e:
            logger.error(f"Не удалось открыть таблицу {self.spreadsheet_id}: {e}")
            raise

    def _get_or_create_worksheet(self, cycle_id: int) -> gspread.Worksheet:
        title = f"Цикл {cycle_id}"
        try:
            ws = self.doc.worksheet(title)
        except gspread.WorksheetNotFound:
            logger.info(f"Лист '{title}' не найден. Создаю новый...")
            ws = self.doc.add_worksheet(title=title, rows=500, cols=15)

            headers = [
                "Дата", "Упражнение",
                "П1: Вес", "П1: Разы",
                "П2: Вес", "П2: Разы",
                "П3: Вес", "П3: Разы",
                "П4: Вес", "П4: Разы",
                "П5: Вес", "П5: Разы"
            ]

            ws.update("B2:M2", [headers])
            ws.format("B2:M2", HEADER_FORMAT)
            ws.freeze(rows=2)

        return ws

    def export_set(self, cycle_id: int, exercise_name: str, set_num: int, weight: float, reps: int,
                   date_str: str) -> bool:
        try:
            ws = self._get_or_create_worksheet(cycle_id)
            cycle_exercises = EXERCISES[cycle_id]

            col_b = ws.col_values(2)
            col_c = ws.col_values(3)

            day_start_row = None

            for i in range(len(col_b) - 1, 0, -1):
                if col_b[i] == date_str:
                    day_start_row = i + 1
                    break

            if not day_start_row:
                start_row = max(3, len(col_c) + 1)
                end_row = start_row + len(cycle_exercises) - 1

                rows_to_insert = []
                for idx, ex in enumerate(cycle_exercises):
                    date_val = date_str if idx == 0 else ""
                    rows_to_insert.append([date_val, ex])

                ws.update(f"B{start_row}:C{end_row}", rows_to_insert)
                ws.merge_cells(f"B{start_row}:B{end_row}")

                formats = [
                    {"range": f"B{start_row}:B{end_row}", "format": DATE_FORMAT},
                    {"range": f"C{end_row}", "format": EXERCISE_LAST_ROW_FORMAT},
                    {"range": f"D{end_row}:M{end_row}", "format": DATA_LAST_ROW_FORMAT}
                ]

                if end_row > start_row:
                    formats.append({"range": f"C{start_row}:C{end_row - 1}", "format": EXERCISE_FORMAT})
                    formats.append({"range": f"D{start_row}:M{end_row - 1}", "format": DATA_FORMAT})

                for col in ["E", "G", "I", "K", "M"]:
                    formats.append({"range": f"{col}{start_row}:{col}{end_row}", "format": REPS_FORMAT})

                ws.batch_format(formats)
                day_start_row = start_row

            try:
                ex_offset = cycle_exercises.index(exercise_name)
                target_row_idx = day_start_row + ex_offset
            except ValueError:
                logger.error(f"Упражнение {exercise_name} не найдено в списке!")
                return False

            col_weight = 4 + (set_num - 1) * 2
            col_reps = col_weight + 1

            cell_weight_a1 = rowcol_to_a1(target_row_idx, col_weight)
            cell_reps_a1 = rowcol_to_a1(target_row_idx, col_reps)

            ws.update(f"{cell_weight_a1}:{cell_reps_a1}", [[weight, reps]])

            logger.info(f"Экспорт: {exercise_name} (Подход {set_num}) - {weight}x{reps} на {date_str}")
            return True

        except Exception as e:
            logger.error(f"Ошибка экспорта в Google Sheets: {e}")
            return False

def export_to_sheets(sheet_id: str, cycle_id: int, exercise_name: str, set_num: int, weight: float, reps: int,
                     date_str: str) -> bool:
    doc = GymSpreadsheet(sheet_id)
    return doc.export_set(cycle_id, exercise_name, set_num, weight, reps, date_str)