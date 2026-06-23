import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import io
import time
from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseUpload
from google.oauth2.service_account import Credentials
from gspread.utils import rowcol_to_a1

from app.core.config import config
from app.core.database import db
from app.core.logger import logger
from app.bot.keyboards import EXERCISES
from app.exporters.spreadsheet import GymSpreadsheet


def create_chart(dates, weights, title):
    plt.figure(figsize=(6, 4))
    plt.plot(dates, weights, marker='o', linestyle='-', color='#1f77b4', linewidth=2, markersize=8)

    plt.title(title, fontsize=14, pad=15, fontweight='bold')
    plt.xlabel('Даты', fontsize=10, fontweight='bold', color='gray')
    plt.ylabel('Вес (кг)', fontsize=10, fontweight='bold', color='gray')
    plt.grid(True, linestyle='--', alpha=0.7)
    plt.xticks(rotation=45, ha='right')
    plt.tight_layout()

    buf = io.BytesIO()
    plt.savefig(buf, format='png', dpi=100)
    plt.close()
    buf.seek(0)
    return buf


def upload_to_drive(buf, filename):
    scopes = ["https://www.googleapis.com/auth/drive"]
    creds = Credentials.from_service_account_file(config.GOOGLE_CREDS_PATH, scopes=scopes)
    service = build('drive', 'v3', credentials=creds)

    file_metadata = {'name': filename}
    media = MediaIoBaseUpload(buf, mimetype='image/png', resumable=True)

    file = service.files().create(body=file_metadata, media_body=media, fields='id').execute()
    file_id = file.get('id')

    service.permissions().create(
        fileId=file_id,
        body={'type': 'anyone', 'role': 'reader'}
    ).execute()

    return f'https://drive.google.com/uc?id={file_id}'


def render_charts_for_user(who='me'):
    user_name = 'Я' if who == 'me' else 'Друг'
    logger.info(f"Начинаю полную перерисовку графиков для: {user_name}")

    sheet_id = config.SPREADSHEET_ID_ME if who == 'me' else config.SPREADSHEET_ID_FRIEND
    gym_doc = GymSpreadsheet(sheet_id)

    try:
        ws = gym_doc.doc.worksheet("Графики")
    except:
        logger.info("Лист 'Графики' не найден. Создаю новый...")
        ws = gym_doc.doc.add_worksheet(title="Графики", rows=10, cols=5)

    requests = [
        {"updateDimensionProperties": {
            "range": {"sheetId": ws.id, "dimension": "COLUMNS", "startIndex": 0, "endIndex": 3},
            "properties": {"pixelSize": 500}, "fields": "pixelSize"}},
        {"updateDimensionProperties": {"range": {"sheetId": ws.id, "dimension": "ROWS", "startIndex": 1, "endIndex": 7},
                                       "properties": {"pixelSize": 350}, "fields": "pixelSize"}}
    ]
    gym_doc.doc.batch_update({"requests": requests})

    matrix = [["Цикл 1", "Цикл 2", "Цикл 3"]]

    for ex_idx in range(6):
        row = []
        for cycle in [1, 2, 3]:
            ex_name = EXERCISES[cycle][ex_idx]

            with db._get_connection() as conn:
                cursor = conn.execute("""
                    SELECT workout_date, MAX(weight) 
                    FROM workout_logs 
                    WHERE who = ? AND cycle = ? AND exercise = ?
                    GROUP BY workout_date
                    ORDER BY MIN(id) ASC
                """, (who, cycle, ex_name))
                data = cursor.fetchall()

            if not data or len(data) < 2:
                row.append("Мало данных для графика")
                continue

            dates = [d[0][:5] for d in data]
            weights = [d[1] for d in data]

            logger.info(f"Отрисовка: Цикл {cycle} | {ex_name} ({len(dates)} точек)")
            buf = create_chart(dates, weights, ex_name)
            url = upload_to_drive(buf, f"chart_{who}_{cycle}_{ex_idx}.png")
            row.append(f'=IMAGE("{url}")')
            time.sleep(1.5)

        matrix.append(row)

    ws.update(range_name='A1:C7', values=matrix, value_input_option='USER_ENTERED')
    ws.format("A1:C1", {
        "backgroundColor": {"red": 0.9, "green": 0.9, "blue": 0.9},
        "textFormat": {"bold": True, "fontSize": 12},
        "horizontalAlignment": "CENTER"
    })
    logger.info(f"Графики для {user_name} успешно обновлены!")


def update_single_chart(who: str, cycle: int, ex_idx: int, ex_name: str):
    logger.info(f"Запрос на фоновое обновление графика: {ex_name}")
    sheet_id = config.SPREADSHEET_ID_ME if who == 'me' else config.SPREADSHEET_ID_FRIEND
    gym_doc = GymSpreadsheet(sheet_id)

    try:
        ws = gym_doc.doc.worksheet("Графики")
    except:
        render_charts_for_user(who)
        return

    with db._get_connection() as conn:
        cursor = conn.execute("""
            SELECT workout_date, MAX(weight) 
            FROM workout_logs 
            WHERE who = ? AND cycle = ? AND exercise = ?
            GROUP BY workout_date
            ORDER BY MIN(id) ASC
        """, (who, cycle, ex_name))
        data = cursor.fetchall()

    if not data or len(data) < 2:
        return

    dates = [d[0][:5] for d in data]
    weights = [d[1] for d in data]

    buf = create_chart(dates, weights, ex_name)
    url = upload_to_drive(buf, f"chart_{who}_{cycle}_{ex_idx}_{int(time.time())}.png")

    cell_a1 = rowcol_to_a1(ex_idx + 2, cycle)

    ws.update(range_name=cell_a1, values=[[f'=IMAGE("{url}")']], value_input_option='USER_ENTERED')
    logger.info(f"График '{ex_name}' обновлен в ячейке {cell_a1}!")


if __name__ == "__main__":
    render_charts_for_user('me')
    render_charts_for_user('friend')