import string

import pytest

from src.embeddings.chunking import chunk_text


def test_chunk_text_empty_string_returns_empty_list():
    assert chunk_text("") == []


def test_chunk_text_whitespace_only_returns_empty_list():
    assert chunk_text("   \n\t  ") == []


def test_chunk_text_raises_when_overlap_equals_chunk_size():
    with pytest.raises(ValueError):
        chunk_text("some text", chunk_size=100, chunk_overlap=100)


def test_chunk_text_raises_when_overlap_greater_than_chunk_size():
    with pytest.raises(ValueError):
        chunk_text("some text", chunk_size=100, chunk_overlap=150)


def test_chunk_text_shorter_than_chunk_size_returns_single_chunk():
    assert chunk_text("hello world", chunk_size=1000, chunk_overlap=100) == ["hello world"]


def test_chunk_text_strips_surrounding_whitespace():
    assert chunk_text("  hello world  \n", chunk_size=1000, chunk_overlap=100) == ["hello world"]


def test_chunk_text_exact_chunk_size_returns_single_chunk():
    text = "a" * 10

    assert chunk_text(text, chunk_size=10, chunk_overlap=3) == [text]


def test_chunk_text_splits_into_overlapping_chunks():
    text = string.ascii_lowercase[:25]

    chunks = chunk_text(text, chunk_size=10, chunk_overlap=3)

    assert chunks == ["abcdefghij", "hijklmnopq", "opqrstuvwx", "vwxy"]


def test_chunk_text_consecutive_chunks_overlap_by_requested_amount():
    text = string.ascii_lowercase[:25]

    chunks = chunk_text(text, chunk_size=10, chunk_overlap=3)

    for previous, current in zip(chunks, chunks[1:]):
        assert previous[-3:] == current[:3]


def test_chunk_text_works_with_default_arguments():
    chunks = chunk_text("short text")

    assert chunks == ["short text"]
