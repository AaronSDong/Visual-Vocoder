def load_settings():  # Taken From AI
    """Load settings from a text file and return as a dictionary."""
    settings = {}
    settings_file = 'settings.txt'
    try:
        with open(settings_file, 'r') as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#'):
                    key, value = line.split('=')
                    key = key.strip()
                    try:
                        # Try to convert to float first
                        settings[key] = float(value.strip())
                    except ValueError:
                        # If that fails, keep as string
                        settings[key] = value.strip()
    except FileNotFoundError:
        print(f"Warning: {settings_file} not found. Using default values.")
    return settings

def update_settings_file(key, value):  # Taken from AI
    """Update a specific setting in the settings file."""
    settings_file = 'settings.txt'
    settings = load_settings()
    settings[key] = value

    try:
        with open(settings_file, 'w') as f:
            for key, val in settings.items():
                f.write(f"{key}={val}\n")
    except Exception as e:
        print(f"Error writing to settings file: {e}")