import calendar
from datetime import datetime
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton

MONTH_NAMES = ["Январь", "Февраль", "Март", "Апрель", "Май", "Июнь",
               "Июль", "Август", "Сентябрь", "Октябрь", "Ноябрь", "Декабрь"]


def get_calendar_kb(year: int, month: int) -> InlineKeyboardMarkup:
    kb = InlineKeyboardMarkup(row_width=7)

    kb.row(
        InlineKeyboardButton("◀️", callback_data=f"cal_prev_{year}_{month}"),
        InlineKeyboardButton(f"{MONTH_NAMES[month - 1]} {year}", callback_data="none"),
        InlineKeyboardButton("▶️", callback_data=f"cal_next_{year}_{month}")
    )

    days = ["Пн", "Вт", "Ср", "Чт", "Пт", "Сб", "Вс"]
    kb.row(*[InlineKeyboardButton(day, callback_data="none") for day in days])

    month_calendar = calendar.monthcalendar(year, month)
    for week in month_calendar:
        row = []
        for day in week:
            if day == 0:
                row.append(InlineKeyboardButton(" ", callback_data="none"))
            else:
                row.append(InlineKeyboardButton(str(day), callback_data=f"cal_day_{year}_{month}_{day}"))
        kb.row(*row)

    kb.add(InlineKeyboardButton("❌ Отмена", callback_data="cal_cancel"))
    return kb