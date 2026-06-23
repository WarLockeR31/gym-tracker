import telebot
import threading
from app.exporters.charts import update_single_chart
from datetime import datetime
from app.core.config import config
from app.core.database import db
from app.bot.keyboards import (
    get_cycles_kb, get_exercises_kb, get_input_kb, EXERCISES,
    get_weight_grid_kb, get_set_grid_kb, get_reps_grid_kb
)
from app.bot.calendar import get_calendar_kb
from app.exporters.spreadsheet import export_to_sheets

bot = telebot.TeleBot(config.BOT_TOKEN)


@bot.message_handler(commands=['start', 'workout'])
def start_workout(message):
    bot.send_message(
        message.chat.id,
        "Выбери цикл тренировки:",
        reply_markup=get_cycles_kb()
    )


@bot.callback_query_handler(func=lambda call: True)
def handle_callbacks(call):
    chat_id = call.message.chat.id
    msg_id = call.message.message_id
    data = call.data

    if data == "none":
        bot.answer_callback_query(call.id)
        return

    if data == "back_to_cycles":
        bot.edit_message_text("Выбери цикл тренировки:", chat_id, msg_id, reply_markup=get_cycles_kb())

    elif data.startswith("cycle_"):
        cycle = int(data.split("_")[1])
        bot.edit_message_text(f"Цикл {cycle}. Выбери упражнение:", chat_id, msg_id,
                              reply_markup=get_exercises_kb(cycle))

    elif data.startswith("back_to_ex_"):
        cycle = int(data.split("_")[3])
        bot.edit_message_text(f"Цикл {cycle}. Выбери упражнение:", chat_id, msg_id,
                              reply_markup=get_exercises_kb(cycle))

    elif data.startswith("ex_"):
        _, cycle, ex = data.split("_")
        today_str = datetime.now().strftime("%d.%m.%Y")

        db.save_state(msg_id, chat_id, cycle=int(cycle), exercise=int(ex), set_num=1, weight=0.0, reps=15,
                      target_date=today_str)
        state = db.get_state(msg_id)
        ex_name = EXERCISES[state['cycle']][state['ex'] - 1]

        text = f"🏋️ **{ex_name}**\nНастрой параметры и запиши подход:"
        bot.edit_message_text(text, chat_id, msg_id, reply_markup=get_input_kb(state), parse_mode="Markdown")

    elif data == "open_calendar":
        now = datetime.now()
        bot.edit_message_text("Выберите дату тренировки:", chat_id, msg_id,
                              reply_markup=get_calendar_kb(now.year, now.month))
        return

    elif data == "cal_cancel":
        state = db.get_state(msg_id)
        ex_name = EXERCISES[state['cycle']][state['ex'] - 1]
        text = f"🏋️ **{ex_name}**\nНастрой параметры и запиши подход:"
        bot.edit_message_text(text, chat_id, msg_id, reply_markup=get_input_kb(state), parse_mode="Markdown")
        return

    elif data.startswith("cal_prev_") or data.startswith("cal_next_"):
        _, direction, year, month = data.split("_")
        year, month = int(year), int(month)

        if direction == "prev":
            month -= 1
            if month < 1:
                month = 12
                year -= 1
        else:
            month += 1
            if month > 12:
                month = 1
                year += 1

        bot.edit_message_text("Выберите дату тренировки:", chat_id, msg_id, reply_markup=get_calendar_kb(year, month))
        return

    elif data.startswith("cal_day_"):
        _, _, year, month, day = data.split("_")
        selected_date = f"{int(day):02d}.{int(month):02d}.{year}"

        state = db.get_state(msg_id)
        state['target_date'] = selected_date
        db.save_state(msg_id, chat_id, state['cycle'], state['ex'], state['set'], state['who'], state['weight'],
                      state['reps'], state['target_date'])

        ex_name = EXERCISES[state['cycle']][state['ex'] - 1]
        text = f"🏋️ **{ex_name}**\nНастрой параметры и запиши подход:"
        bot.edit_message_text(text, chat_id, msg_id, reply_markup=get_input_kb(state), parse_mode="Markdown")
        return

    elif data == "open_weight_grid":
        bot.edit_message_reply_markup(chat_id, msg_id, reply_markup=get_weight_grid_kb())
        return

    elif data == "open_set_grid":
        bot.edit_message_reply_markup(chat_id, msg_id, reply_markup=get_set_grid_kb())
        return

    elif data == "open_reps_grid":
        bot.edit_message_reply_markup(chat_id, msg_id, reply_markup=get_reps_grid_kb())
        return

    elif data == "back_to_input":
        state = db.get_state(msg_id)
        if not state:
            bot.answer_callback_query(call.id, "Ошибка сессии.", show_alert=True)
            return
        bot.edit_message_reply_markup(chat_id, msg_id, reply_markup=get_input_kb(state))
        return

    elif data.startswith("set_grid_"):
        parts = data.split("_")  # ['set', 'grid', 'weight', '80']
        action = parts[2]
        val_str = parts[3]

        state = db.get_state(msg_id)
        if not state:
            bot.answer_callback_query(call.id, "Ошибка сессии. Начни заново /workout", show_alert=True)
            return

        if action == "weight":
            state['weight'] = float(val_str)
        elif action == "set":
            state['set'] = int(val_str)
        elif action == "reps":
            state['reps'] = int(val_str)

        db.save_state(
            msg_id, chat_id, state['cycle'], state['ex'], state['set'],
            state['who'], state['weight'], state['reps'], state['target_date']
        )

        bot.edit_message_reply_markup(chat_id, msg_id, reply_markup=get_input_kb(state))
        return

    elif data.startswith("input_"):
        state = db.get_state(msg_id)
        if not state:
            bot.answer_callback_query(call.id, "Ошибка сессии. Начни заново /workout", show_alert=True)
            return

        action = data.replace("input_", "")

        if action == "who":
            state['who'] = "friend" if state['who'] == "me" else "me"
        elif action == "s_m1":
            state['set'] = max(1, state['set'] - 1)
        elif action == "s_p1":
            state['set'] = min(5, state['set'] + 1)
        elif action == "w_m5":
            state['weight'] = max(0, state['weight'] - 5)
        elif action == "w_p5":
            state['weight'] += 5
        elif action == "w_m1":
            state['weight'] = max(0, state['weight'] - 1)
        elif action == "w_p1":
            state['weight'] += 1
        elif action == "w_m05":
            state['weight'] = max(0, state['weight'] - 0.5)
        elif action == "r_m1":
            state['reps'] = max(0, state['reps'] - 1)
        elif action == "r_p1":
            state['reps'] += 1


        elif action == "save":
            ex_name = EXERCISES[state['cycle']][state['ex'] - 1]
            target_date = state['target_date']
            db.save_log(target_date, state['who'], state['cycle'], ex_name, state['set'], state['weight'],
                        state['reps'])

            target_sheet_id = config.SPREADSHEET_ID_ME if state['who'] == "me" else config.SPREADSHEET_ID_FRIEND

            success = export_to_sheets(
                sheet_id=target_sheet_id,
                cycle_id=state['cycle'],
                exercise_name=ex_name,
                set_num=state['set'],
                weight=state['weight'],
                reps=state['reps'],
                date_str=target_date
            )

            if success:
                bot.answer_callback_query(call.id, f"Подход {state['set']} сохранен!")

                threading.Thread(
                    target=update_single_chart,
                    args=(state['who'], state['cycle'], state['ex'] - 1, ex_name),
                    daemon=True
                ).start()

                state['set'] = min(5, state['set'] + 1)
            else:
                bot.answer_callback_query(call.id, "Ошибка сохранения в таблицу!", show_alert=True)

        db.save_state(
            msg_id, chat_id, state['cycle'], state['ex'], state['set'],
            state['who'], state['weight'], state['reps'], state['target_date']
        )

        ex_name = EXERCISES[state['cycle']][state['ex'] - 1]
        text = f"🏋️ **{ex_name}**\nНастрой параметры и запиши подход:"

        try:
            bot.edit_message_text(text, chat_id, msg_id, reply_markup=get_input_kb(state), parse_mode="Markdown")
        except Exception:
            pass


def run_bot():
    bot.infinity_polling()