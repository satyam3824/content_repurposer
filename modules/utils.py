def save_to_txt(text, filename="output.txt"):
    with open(filename, "w", encoding="utf-8") as f:
        f.write(text)
    return filename
