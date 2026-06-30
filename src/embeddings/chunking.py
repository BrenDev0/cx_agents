def chunk_text(
    text: str,
    chunk_size: int = 1000,
    chunk_overlap: int = 100
) -> list[str]:
    if chunk_overlap >= chunk_size:
        raise ValueError("chunk_overlap must be smaller than chunk_size")

    text = text.strip()

    if not text:
        return []

    step = chunk_size - chunk_overlap
    chunks = []
    start = 0

    while start < len(text):
        chunks.append(text[start:start + chunk_size])
        start += step

    return chunks
