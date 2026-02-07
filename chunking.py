def load_legal_data(path):
    with open(path, "r", encoding="utf-8") as file:
        return file.read()


def chunk_by_section(text):
    lines = text.split("\n")
    chunks = []

    current_chunk = ""
    for line in lines:
        line = line.strip()
        if not line:
            continue

        if line.startswith("IPC Section"):
            if current_chunk:
                chunks.append(current_chunk.strip())
            current_chunk = line
        else:
            current_chunk += " " + line

    if current_chunk:
        chunks.append(current_chunk.strip())

    return chunks


if __name__ == "__main__":
    data = load_legal_data("data/ipc.txt")
    chunks = chunk_by_section(data)

    print(f"Total Chunks Created: {len(chunks)}\n")

    for i, chunk in enumerate(chunks):
        print(f"--- Chunk {i + 1} ---")
        print(chunk)
        print()
