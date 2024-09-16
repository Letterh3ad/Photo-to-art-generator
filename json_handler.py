import json
import tempfile

def load_art_styles(filename='art_styles.json', create_temp_file=False):
    try:
        with open(filename, 'r') as file:
            data = json.load(file)
            if isinstance(data, list):
                # Optionally create a temporary file with the art style descriptions
                if create_temp_file:
                    art_style_description = next(
                        (style['description'] for style in data if isinstance(style, dict) and style.get('name') == self.selected_art_style),
                        None
                    )
                    if art_style_description:
                        # Create a temporary file
                        temp_file_path = tempfile.NamedTemporaryFile(delete=False, mode='w', encoding='utf-8').name
                        with open(temp_file_path, 'w', encoding='utf-8') as temp_file:
                            temp_file.write(art_style_description)
                        return temp_file_path
                    else:
                        print("Selected art style description not found.")
                        return None
                else:
                    return data  # Return as a list of dictionaries
            else:
                print("Unexpected data format in art_styles.json:", data)
                return []
    except FileNotFoundError:
        print("The JSON file was not found.")
        return []
    except json.JSONDecodeError:
        print("Error decoding the JSON file.")
        return []

def update_art_style(name, description, filename='art_styles.json'):
    art_styles = load_art_styles(filename)
    for art_style in art_styles:
        if art_style["name"] == name:
            art_style["description"] = description
            break
    with open(filename, 'w') as file:
        json.dump(art_styles, file, indent=4)

def remove_art_style(name, filename='art_styles.json'):
    art_styles = load_art_styles(filename)
    art_styles = [art_style for art_style in art_styles if art_style["name"] != name]
    with open(filename, 'w') as file:
        json.dump(art_styles, file, indent=4)

def add_art_style(name, description, filename='art_styles.json'):
    art_styles = load_art_styles(filename)
    art_styles.append({"name": name, "description": description})
    with open(filename, 'w') as file:
        json.dump(art_styles, file, indent=4)


