COLOR_GRAY = {"red": 0.9, "green": 0.9, "blue": 0.9}
COLOR_WHITE = {"red": 1.0, "green": 1.0, "blue": 1.0}

BORDER_MEDIUM = {"style": "SOLID_MEDIUM"}
BORDER_THIN = {"style": "SOLID"}

BORDERS_HEADER = {
    "top": BORDER_MEDIUM, "bottom": BORDER_MEDIUM,
    "left": BORDER_MEDIUM, "right": BORDER_MEDIUM
}

BORDERS_DATA_BASE = {
    "top": BORDER_THIN, "bottom": BORDER_THIN,
    "left": BORDER_THIN, "right": BORDER_THIN
}

BORDERS_DATA_LAST_ROW = {
    "top": BORDER_THIN, "bottom": BORDER_MEDIUM,
    "left": BORDER_THIN, "right": BORDER_THIN
}

BORDERS_EXERCISE = {
    "top": BORDER_THIN, "bottom": BORDER_THIN,
    "left": BORDER_THIN, "right": BORDER_MEDIUM
}

BORDERS_EXERCISE_LAST_ROW = {
    "top": BORDER_THIN, "bottom": BORDER_MEDIUM,
    "left": BORDER_THIN, "right": BORDER_MEDIUM
}

BORDERS_REPS = {
    "top": BORDER_MEDIUM, "bottom": BORDER_MEDIUM,
    "left": BORDER_MEDIUM, "right": BORDER_MEDIUM
}

HEADER_FORMAT = {
    "backgroundColor": COLOR_GRAY,
    "textFormat": {"bold": True, "fontSize": 11},
    "horizontalAlignment": "CENTER",
    "verticalAlignment": "MIDDLE",
    "borders": BORDERS_HEADER
}

DATA_FORMAT = {
    "backgroundColor": COLOR_WHITE,
    "horizontalAlignment": "CENTER",
    "verticalAlignment": "MIDDLE",
    "borders": BORDERS_DATA_BASE
}

DATA_LAST_ROW_FORMAT = {
    "backgroundColor": COLOR_WHITE,
    "horizontalAlignment": "CENTER",
    "verticalAlignment": "MIDDLE",
    "borders": BORDERS_DATA_LAST_ROW
}

EXERCISE_FORMAT = {
    "backgroundColor": COLOR_WHITE,
    "horizontalAlignment": "LEFT",
    "verticalAlignment": "MIDDLE",
    "borders": BORDERS_EXERCISE
}

EXERCISE_LAST_ROW_FORMAT = {
    "backgroundColor": COLOR_WHITE,
    "horizontalAlignment": "LEFT",
    "verticalAlignment": "MIDDLE",
    "borders": BORDERS_EXERCISE_LAST_ROW
}

REPS_FORMAT = {
    "backgroundColor": COLOR_WHITE,
    "horizontalAlignment": "CENTER",
    "verticalAlignment": "MIDDLE",
    "textFormat": {"bold": True},
    "borders": BORDERS_REPS
}

DATE_FORMAT = {
    "backgroundColor": COLOR_WHITE,
    "horizontalAlignment": "CENTER",
    "verticalAlignment": "MIDDLE",
    "textFormat": {"bold": True},
    "borders": BORDERS_HEADER
}