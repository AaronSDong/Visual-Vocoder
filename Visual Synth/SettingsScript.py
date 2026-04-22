# dictionaries in this script are likely AI
import json
import numpy as np

SETTINGS_FILE = 'settings.json'
DEFAULT_SETTINGS_FILE = 'default_settings.json'

def load_settings():  # Fully taken From AI
    """Load settings from a JSON file and return as a dictionary."""
    try:
        with open(SETTINGS_FILE, 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        print(f"Warning: {SETTINGS_FILE} not found. Using default values.")
        return {}
    except json.JSONDecodeError as e:
        print(f"Error parsing {SETTINGS_FILE}: {e}")
        return {}

def update_settings_file(key, value):  # Fully taken from AI
    """Update a specific setting in the settings JSON file."""
    settings = load_settings()
    settings[key] = value

    try:
        with open(SETTINGS_FILE, 'w') as f:
            json.dump(settings, f, indent=4)
    except Exception as e:
        print(f"Error writing to settings file: {e}")

def reset_settings_to_default():  # Fully AI
    """Reset settings.json to the default settings from default_settings.json."""
    try:
        with open(DEFAULT_SETTINGS_FILE, 'r') as f:
            default_settings = json.load(f)
        with open(SETTINGS_FILE, 'w') as f:
            json.dump(default_settings, f, indent=4)
    except FileNotFoundError as e:
        print(f"Error: {e}")
    except json.JSONDecodeError as e:
        print(f"Error parsing default settings: {e}")
    except Exception as e:
        print(f"Error resetting settings: {e}")

# ----------------------------------------------------------------------------------------------------------------------

def getScale(scale, key):
    scale_notes = get_scale(scale.lower())
    key_shifter = 2 ** (get_key_index(key) / 12)  # equal temperament factor
    return scale_notes * key_shifter

def get_key_index(key):
    # Index relative to C (going up)
    index = {
        'C': 0, 'B#': 0, 'Dbb': 0,
        'C#': 1, 'Db': 1,
        'D': 2, 'C##': 2, 'Ebb': 2,
        'D#': 3, 'Eb': 3,
        'E': 4, 'Fb': 4, 'D##': 4,
        'F': 5, 'E#': 5, 'Gbb': 5,
        'F#': 6, 'Gb': 6,
        'G': 7, 'F##': 7, 'Abb': 7,
        'G#': 8, 'Ab': 8,
        'A': 9, 'G##': 9, 'Bbb': 9,
        'A#': 10, 'Bb': 10,
        'B': 11, 'Cb': 11, 'A##': 11
    }

    return index[key]

def get_key(index):
    # Index relative to C (going up)
    key = {
        0: 'C',
        1: 'C#',
        2: 'D',
        3: 'D#',
        4: 'E',
        5: 'F',
        6: 'F#',
        7: 'G',
        8: 'G#',
        9: 'A',
        10: 'A#',
        11: 'B'
    }

    return key[index]

# ----------------------------------------------------------------------------------------------------------------------

SCALE_NAMES = ["major", "minor", "harmonic", "blues", "dorian", "phrygian", "lydian", "mixolydian", "locrian"]

def get_scale(scale):
    # All scales are in Just Intonation, starting at C4 (list of frequencies)
    scale_list = {
        "major": [256.0, 288.0, 320.0, 341.33, 384.0, 426.67, 480.0, 512.0],
        "minor": [256.0, 288.0, 307.2, 341.33, 384.0, 409.6, 460.8, 512.0],
        "harmonic": [256.0, 288.0, 307.2, 341.33, 384.0, 409.6, 480.0, 512.0],
        "blues": [256.0, 307.2, 341.33, 360.0, 384.0, 426.67, 460.8, 512.0],
        "dorian": [256.0, 288.0, 307.2, 341.33, 384.0, 426.67, 460.8, 512.0],
        "phrygian": [256.0, 273.07, 307.2, 341.33, 384.0, 409.6, 460.8, 512.0],
        "lydian": [256.0, 288.0, 320.0, 360.0, 384.0, 426.67, 480.0, 512.0],
        "mixolydian": [256.0, 288.0, 320.0, 341.33, 384.0, 426.67, 460.8, 512.0],
        "locrian": [256.0, 273.07, 307.2, 341.33, 364.09, 409.6, 460.8, 512.0]
    }

    return np.array(scale_list[scale])

def get_scale_index(scale):
    return SCALE_NAMES.index(scale)

def get_scale_from_index(index):
    return SCALE_NAMES[index]

# ----------------------------------------------------------------------------------------------------------------------

WAVE_SHAPES = ['sine', 'square', 'sawtooth', 'triangle', 'custom']

def get_wave_shape_index(shape):  # AI
    return WAVE_SHAPES.index(shape) if shape in WAVE_SHAPES else 0

def change_wave_shape(change):  # AI
    settings = load_settings()
    current_shape = settings['wave_shape']

    new_shape_index = (get_wave_shape_index(current_shape) + change) % len(WAVE_SHAPES)
    new_shape = WAVE_SHAPES[new_shape_index]
    update_settings_file('wave_shape', new_shape)