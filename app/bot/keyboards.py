from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton
from datetime import datetime, timedelta

EXERCISES = {
    1: ["Тяга верхнего блока", "Сведение рук в тренажёре", "Жим сидя в тренажёре", "Разгибание на трицепс в верхнем блоке", "Подъём на бицепс в блоке", "Жим ногами"],
    2: ["Жим на верхнюю часть груди в тренажёре Смита", "Рычажная тяга для мышц спины", "Подъём гантелей через стороны (плечи)", "Подъём гантелей на бицепс сидя", "Отжимания от скамьи для трицепса", "Разгибание голени сидя (квадрицепс)"],
    3: ["Жим от груди в тренажёре сидя", "Горизонтальная тяга для мышц спины", "Жим в тренажёре Смита сидя для плеч (перед собой)", "Жим узким хватом на трицепс в Смите", "Подъём гантелей «молоток» на бицепс сидя", "Приседание в гак-машине"]
}

def get_cycles_kb():
    kb = InlineKeyboardMarkup(row_width=1)
    kb.add(
        InlineKeyboardButton("Цикл 1", callback_data="cycle_1"),
        InlineKeyboardButton("Цикл 2", callback_data="cycle_2"),
        InlineKeyboardButton("Цикл 3", callback_data="cycle_3")
    )
    return kb

def get_exercises_kb(cycle_id: int):
    kb = InlineKeyboardMarkup(row_width=2)
    buttons = []
    for i, ex_name in enumerate(EXERCISES[cycle_id], start=1):
        buttons.append(InlineKeyboardButton(ex_name, callback_data=f"ex_{cycle_id}_{i}"))
    kb.add(*buttons)
    kb.add(InlineKeyboardButton("⬅️ Назад", callback_data="back_to_cycles"))
    return kb

def get_input_kb(state: dict):
    kb = InlineKeyboardMarkup(row_width=3)

    date_display = state['target_date']
    if date_display == datetime.now().strftime("%d.%m.%Y"):
        date_display = "Сегодня"
    kb.add(InlineKeyboardButton(f"📅 Дата: {date_display}", callback_data="open_calendar"))

    kb.row(
        InlineKeyboardButton("◀️ Подход", callback_data="input_s_m1"),
        InlineKeyboardButton(f"🔢 Подход {state['set']}", callback_data="open_set_grid"),
        InlineKeyboardButton("Подход ▶️", callback_data="input_s_p1")
    )

    who_text = "👤 Рома" if state['who'] == "me" else "👤 Паша"
    kb.add(InlineKeyboardButton(f"Кто делает: {who_text} 🔄", callback_data="input_who"))

    kb.row(
        InlineKeyboardButton("-5 кг", callback_data="input_w_m5"),
        InlineKeyboardButton(f"⚖️ {state['weight']} кг", callback_data="open_weight_grid"),
        InlineKeyboardButton("+5 кг", callback_data="input_w_p5")
    )
    kb.row(
        InlineKeyboardButton("-1 кг", callback_data="input_w_m1"),
        InlineKeyboardButton("-0.5 кг", callback_data="input_w_m05"),
        InlineKeyboardButton("+1 кг", callback_data="input_w_p1")
    )

    kb.row(
        InlineKeyboardButton("-1 раз", callback_data="input_r_m1"),
        InlineKeyboardButton(f"🔄 {state['reps']} раз", callback_data="open_reps_grid"),
        InlineKeyboardButton("+1 раз", callback_data="input_r_p1")
    )

    kb.add(InlineKeyboardButton("✅ ЗАПИСАТЬ ПОДХОД", callback_data="input_save"))
    kb.add(InlineKeyboardButton("⬅️ Назад к упражнениям", callback_data=f"back_to_ex_{state['cycle']}"))

    return kb

def get_weight_grid_kb():
    kb = InlineKeyboardMarkup(row_width=3)
    weights = [10, 20, 30, 40, 50, 60, 70, 80, 90, 100]
    buttons = [InlineKeyboardButton(f"{w} кг", callback_data=f"set_grid_weight_{w}") for w in weights]
    kb.add(*buttons)
    kb.add(InlineKeyboardButton("⬅️ Назад", callback_data="back_to_input"))
    return kb

def get_set_grid_kb():
    kb = InlineKeyboardMarkup(row_width=5)
    buttons = [InlineKeyboardButton(f"{s}", callback_data=f"set_grid_set_{s}") for s in range(1, 6)]
    kb.add(*buttons)
    kb.add(InlineKeyboardButton("⬅️ Назад", callback_data="back_to_input"))
    return kb

def get_reps_grid_kb():
    kb = InlineKeyboardMarkup(row_width=3)
    buttons = [InlineKeyboardButton(f"{r}", callback_data=f"set_grid_reps_{r}") for r in range(10, 16)]
    kb.add(*buttons)
    kb.add(InlineKeyboardButton("⬅️ Назад", callback_data="back_to_input"))
    return kb