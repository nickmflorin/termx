INDENT_COUNT = 2
COLOR_DEPTH = 256
DATE_FORMAT = '%Y-%m-%d %H:%M:%S'

ANSI_ESCAPE_CHAR = "\x1b"
STRICT_CONFIG = True


ICONS = {
    "NOTSET": "",

    "SKULL": "☠",
    "CROSS": "✘",
    "CHECK": "✔",
    "TACK": "📌",
    "GEAR": "⚙️ ",
    "CROSSING": "🚧",

    "FAIL": "CROSS",
    "SUCCESS": "CHECK",
    "WARNING": "CROSS",

    "DEBUG": "GEAR",
    "INFO": "TACK",
    "ERROR": "CROSS",
    "CRITICAL": "SKULL",
}

STYLES = {

}

COLORS = {
    "GREEN": "#28A745",
    "LIGHT_GREEN": "DarkOliveGreen3",

    "RED": "#DC3545",
    "ALT_RED": "Red1",
    "LIGHT_RED": "IndianRed",

    "YELLOW": "Gold3",
    "LIGHT_YELLOW": "LightYellow3",

    "BLUE": "#007bff",
    "DARK_BLUE": "#336699",
    "CORNFLOWER_BLUE": "CornflowerBlue",
    "ROYAL_BLUE": "RoyalBlue1",

    "PURPLE": "#364652",
    "ORANGE": "#EDAE49",

    "HEAVY_BLACK": "#000000",
    "OFF_BLACK": "#151515",
    "LIGHT_BLACK": "#2A2A2A",
    "EXTRA_LIGHT_BLACK": "#3F3F3F",

    "DARK_GRAY": "#545454",
    "NORMAL_GRAY": "#696969",
    "LIGHT_GRAY": "#A8A8A8",
    "EXTRA_LIGHT_GRAY": "#DBDBDB",
    "FADED_GRAY": "#D7D7D7",

    "FAIL": "RED",
    "SUCCESS": "GREEN",
    "WARNING": "YELLOW",
    "NOTSET": "NORMAL_GRAY",

    "CRITICAL": "RED",
    "ERROR": "RED",
    "INFO": "BLUE",
    "DEBUG": "NORMAL_GRAY",

    "SHADES": [
        "HEAVY_BLACK",
        "OFF_BLACK",
        "LIGHT_BLACK",
        "EXTRA_LIGHT_BLACK",
        "DARK_GRAY",
        "NORMAL_GRAY",
        "LIGHT_GRAY",
        "EXTRA_LIGHT_GRAY",
        "FADED_GRAY",
    ]
}

FORMATS = {
    "CRITICAL": {
        "COLOR": COLORS["CRITICAL"],
        "ICON": ICONS["CRITICAL"],
        "STYLES": "BOLD",
    },
    "FAIL": {
        "COLOR": COLORS["FAIL"],
        "ICON": ICONS["FAIL"],
    },
    "SUCCESS": {
        "COLOR": COLORS["SUCCESS"],
        "ICON": ICONS["SUCCESS"],
    },
    "WARNING": {
        "COLOR": COLORS["WARNING"],
        "ICON": ICONS["WARNING"],
    },
    "INFO": {
        "COLOR": COLORS["INFO"],
        "ICON": ICONS["INFO"],
    },
    "DEBUG": {
        "COLOR": COLORS["DEBUG"],
        "ICON": ICONS["DEBUG"],
    },
    "NOTSET": {
        "COLOR": COLORS["NOTSET"],
        "ICON": ICONS["NOTSET"],
    },
}

TEXT = {
    "NORMAL": {
        "COLOR": "OFF_BLACK",
    },
    "EMPHASIS": {
        "COLOR": "HEAVY_BLACK",
    },
    "PRIMARY": {
        "COLOR": "LIGHT_BLACK",
    },
    "MEDIUM": {
        "COLOR": "NORMAL_GRAY",
    },
    "LIGHT": {
        "COLOR": "LIGHT_GRAY",
    },
    "EXTRA_LIGHT": {
        "COLOR": "EXTRA_LIGHT_GRAY",
    },
    "FADED": {
        "COLOR": "LIGHT_YELLOW",
    },
}
