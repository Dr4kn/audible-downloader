from audibleDownloader import MetadataGuesser, Status
import pytest
import os
from pathlib import Path


def test_basic_parsing():
    assert 5 == MetadataGuesser("Harry Potter and the Order of the Phoenix", "Harry Potter, Book 5", "Harry Potter").get_series_sequence()
    assert 4 == MetadataGuesser("Cibola Burn", "Book 4 of the Expanse", "Expanse").get_series_sequence()
    assert 4 == MetadataGuesser("Cibola Burn", "Book 4, of the Expanse", "Expanse").get_series_sequence()
    assert 4 == MetadataGuesser("Cibola Burn", "Book 4. of the Expanse", "Expanse").get_series_sequence()
    assert 4.5 == MetadataGuesser("Cibola Burn", "Book 4.5 of the Expanse", "Expanse").get_series_sequence()
    assert 4.5 == MetadataGuesser("Cibola Burn", "Book 4,5 of the Expanse", "Expanse").get_series_sequence()
    assert None == MetadataGuesser("Cibola Burn", "Book 4 of the Expanse", "Expanses").get_series_sequence()
    assert None == MetadataGuesser("Cibola Burn", "Book 4 of the Expanse", "of this").get_series_sequence()
    assert 4 == MetadataGuesser("Cibola Burn", "Book 4 of the Expanse", "of the").get_series_sequence()
    metadata_guesser = MetadataGuesser("Cibola Burn", "Book 4 of the Expanse", "Expanse")
    assert Status.SUCCESS == metadata_guesser.guess_missing_data()
    assert 4 == metadata_guesser.get_series_sequence()

def test_roman_numeral_parsing():
    assert 2 == MetadataGuesser("Cool Name", "Book II of the Interesting Trilogy", "Interesting").get_series_sequence()
    assert 9 == MetadataGuesser("Cool Name", "Book IX of the Interesting Trilogy", "Interesting").get_series_sequence()
    assert 12 == MetadataGuesser("Cool Name", "Book XII of the Interesting Trilogy", "Interesting").get_series_sequence()
    assert 2 == MetadataGuesser("Cool Name", "Book II, of the Interesting Trilogy", "Interesting").get_series_sequence()
    

def test_english_number_parsing():
    assert 6 == MetadataGuesser("Babylon's Ashes", "Book Six of the Expanse", "Expanse").get_series_sequence()
    assert 6 == MetadataGuesser("Babylon's Ashes", "The Expanse, Book Six", "Expanse").get_series_sequence()
    assert 6 == MetadataGuesser("Babylon's Ashes", "The Expanse,Book Six", "Expanse").get_series_sequence()
    assert 6 == MetadataGuesser("Babylon's Ashes", "Book ,Six of the Expanse", "Expanse").get_series_sequence()

def test_symbol_removing():
    assert 6 == MetadataGuesser("Babylon's Ashes", "Book (Six) of the Expanse", "Expanse").get_series_sequence()
    assert 6 == MetadataGuesser("Babylon's Ashes", "Book [Six] of the Expanse", "Expanse").get_series_sequence()
    assert 6 == MetadataGuesser("Babylon's Ashes", "Book ,Six. of the Expanse", "Expanse").get_series_sequence()
    assert 6 == MetadataGuesser("Babylon's Ashes", "Book ;Six| of the Expanse", "Expanse").get_series_sequence()
    assert 6 == MetadataGuesser("Babylon's Ashes", "Book \{Six\} of the Expanse", "Expanse").get_series_sequence()
    assert 6 == MetadataGuesser("Babylon's Ashes", "Book \{Six\} of the Expanse", "Expanse").get_series_sequence()
    assert 6 == MetadataGuesser("Babylon's Ashes", "Book \Six/ of the Expanse", "Expanse").get_series_sequence()
    
# def test_series_name_missing():
#     assert 1 == get_series_sequence("Foundation", "The Foundation Trilogy, Book 1", None)

# def test_subtitle_missing():
#     assert 1 == get_series_sequence("Dune", None, "Dune")