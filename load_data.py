def load_legal_data(path):
    with open(path, "r", encoding="utf-8") as file:
        return file.read()


if __name__ == "__main__":
    data = load_legal_data("data/ipc.txt")
    print("Legal Data Loaded Successfully\n")
    print(data)
