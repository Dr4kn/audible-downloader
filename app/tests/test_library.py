from audibleDownloader.library import get_series_sequence
import pytest
import os
from pathlib import Path


def test_basic_parsing():
    assert 5 == get_series_sequence("Harry Potter and the Order of the Phoenix", "Harry Potter, Book 5", "Harry Potter")
    assert 4 == get_series_sequence("Cibola Burn", "Book 4 of the Expanse", "Expanse")
    assert 4 == get_series_sequence("Cibola Burn", "Book 4, of the Expanse", "Expanse")
    assert 4 == get_series_sequence("Cibola Burn", "Book 4. of the Expanse", "Expanse")
    assert 4.5 == get_series_sequence("Cibola Burn", "Book 4.5 of the Expanse", "Expanse")
    assert 4.5 == get_series_sequence("Cibola Burn", "Book 4,5 of the Expanse", "Expanse")
    assert None == get_series_sequence("Cibola Burn", "Book 4 of the Expanse", "Expanses")
    assert None == get_series_sequence("Cibola Burn", "Book 4 of the Expanse", "of this")
    assert 4 == get_series_sequence("Cibola Burn", "Book 4 of the Expanse", "of the")

def test_roman_numeral_parsing():
    assert 2 == get_series_sequence("Cool Name", "Book II of the Interesting Trilogy", "Interesting")
    assert 9 == get_series_sequence("Cool Name", "Book IX of the Interesting Trilogy", "Interesting")
    assert 12 == get_series_sequence("Cool Name", "Book XII of the Interesting Trilogy", "Interesting")
    assert 2 == get_series_sequence("Cool Name", "Book II, of the Interesting Trilogy", "Interesting")

def test_english_number_parsing():
    assert 6 == get_series_sequence("Babylon's Ashes", "Book Six of the Expanse", "Expanse")
    assert 6 == get_series_sequence("Babylon's Ashes", "The Expanse, Book Six", "Expanse")


# def test_series_name_missing():
#     assert 1 == get_series_sequence("Foundation", "The Foundation Trilogy, Book 1", None)

# def test_subtitle_missing():
#     assert 1 == get_series_sequence("Dune", None, "Dune")