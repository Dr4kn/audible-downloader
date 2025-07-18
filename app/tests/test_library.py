from audibleDownloader import MetadataGuesser, Status
import pytest
import os
from pathlib import Path


def test_basic_parsing():
    metadata_guesser = MetadataGuesser("Harry Potter and the Order of the Phoenix", "Harry Potter, Book 5", "Harry Potter")
    metadata_guesser.guess_missing_data()
    assert 5 == metadata_guesser.get_series_sequence()

    metadata_guesser = MetadataGuesser("Cibola Burn", "Book 4 of the Expanse", "Expanse")
    metadata_guesser.guess_missing_data()
    assert 4 == metadata_guesser.get_series_sequence()
    
    metadata_guesser = MetadataGuesser("Cibola Burn", "Book 4, of the Expanse", "Expanse")
    metadata_guesser.guess_missing_data()
    assert 4 == metadata_guesser.get_series_sequence()

    metadata_guesser = MetadataGuesser("Cibola Burn", "Book 4. of the Expanse", "Expanse")
    metadata_guesser = MetadataGuesser("Cibola Burn", "Book 4.5 of the Expanse", "Expanse")
    metadata_guesser.guess_missing_data()
    assert 4.5 == metadata_guesser.get_series_sequence()

    metadata_guesser = MetadataGuesser("Cibola Burn", "Book 4,5 of the Expanse", "Expanse")
    metadata_guesser.guess_missing_data()
    assert 4.5 == metadata_guesser.get_series_sequence()

    metadata_guesser = MetadataGuesser("Cibola Burn", "Book 4 of the Expanse", "Expanses")
    metadata_guesser.guess_missing_data()
    assert None == metadata_guesser.get_series_sequence()

    metadata_guesser = MetadataGuesser("Cibola Burn", "Book 4 of the Expanse", "of this")
    metadata_guesser.guess_missing_data()
    assert None == metadata_guesser.get_series_sequence()

    metadata_guesser = MetadataGuesser("Cibola Burn", "Book 4 of the Expanse", "of the")
    metadata_guesser.guess_missing_data()
    assert 4 == metadata_guesser.get_series_sequence()

    metadata_guesser = MetadataGuesser("Cibola Burn", "Book 4 of the Expanse", "Expanse")
    assert Status.SUCCESS == metadata_guesser.guess_missing_data()
    assert 4 == metadata_guesser.get_series_sequence()

    assert Status.ERROR == MetadataGuesser("Dune", None, None).guess_missing_data()

    metadata_guesser = MetadataGuesser("Cibola Burn", "Expanse", "Expanse")
    assert Status.ERROR == metadata_guesser.guess_missing_data()

def test_roman_numeral_parsing():
    metadata_guesser = MetadataGuesser("Cool Name", "Book II of the Interesting Trilogy", "Interesting")
    metadata_guesser.guess_missing_data()
    assert 2 == metadata_guesser.get_series_sequence()

    metadata_guesser = MetadataGuesser("Cool Name", "Book IX of the Interesting Trilogy", "Interesting")
    metadata_guesser.guess_missing_data()
    assert 9 == metadata_guesser.get_series_sequence()

    metadata_guesser = MetadataGuesser("Cool Name", "Book XII of the Interesting Trilogy", "Interesting")
    metadata_guesser.guess_missing_data()
    assert 12 == metadata_guesser.get_series_sequence()

    metadata_guesser = MetadataGuesser("Cool Name", "Book II, of the Interesting Trilogy", "Interesting")
    metadata_guesser.guess_missing_data()
    assert 2 == metadata_guesser.get_series_sequence()
    

def test_english_number_parsing():
    metadata_guesser = MetadataGuesser("Babylon's Ashes", "Book Six of the Expanse", "Expanse")
    metadata_guesser.guess_missing_data()
    assert 6 == metadata_guesser.get_series_sequence()

    metadata_guesser = MetadataGuesser("Babylon's Ashes", "The Expanse, Book Six", "Expanse")
    metadata_guesser.guess_missing_data()
    assert 6 == metadata_guesser.get_series_sequence()

    metadata_guesser = MetadataGuesser("Babylon's Ashes", "The Expanse,Book Six", "Expanse")
    metadata_guesser.guess_missing_data()
    assert 6 == metadata_guesser.get_series_sequence()

    metadata_guesser = MetadataGuesser("Babylon's Ashes", "Book ,Six of the Expanse", "Expanse")
    metadata_guesser.guess_missing_data()
    assert 6 == metadata_guesser.get_series_sequence()

def test_symbol_removing():
    metadata_guesser = MetadataGuesser("Babylon's Ashes", "Book (Six) of the Expanse", "Expanse")
    metadata_guesser.guess_missing_data()
    assert 6 == metadata_guesser.get_series_sequence()

    metadata_guesser = MetadataGuesser("Babylon's Ashes", "Book [Six] of the Expanse", "Expanse")
    metadata_guesser.guess_missing_data()
    assert 6 == metadata_guesser.get_series_sequence()

    metadata_guesser = MetadataGuesser("Babylon's Ashes", "Book ,Six. of the Expanse", "Expanse")
    metadata_guesser.guess_missing_data()
    assert 6 == metadata_guesser.get_series_sequence()

    metadata_guesser = MetadataGuesser("Babylon's Ashes", "Book ;Six| of the Expanse", "Expanse")
    metadata_guesser.guess_missing_data()
    assert 6 == metadata_guesser.get_series_sequence()

    metadata_guesser = MetadataGuesser("Babylon's Ashes", "Book {Six} of the Expanse", "Expanse")
    metadata_guesser.guess_missing_data()
    assert 6 == metadata_guesser.get_series_sequence()

    metadata_guesser = MetadataGuesser("Babylon's Ashes", "Book \\Six/ of the Expanse", "Expanse")
    metadata_guesser.guess_missing_data()
    assert 6 == metadata_guesser.get_series_sequence()
    
def test_subtitle_missing():
    metadata_guesser = MetadataGuesser("Dune", None, "Dune")
    assert Status.SUCCESS == metadata_guesser.guess_missing_data()
    assert "Dune 1" == metadata_guesser.get_subtitle()
    assert 1 == metadata_guesser.get_series_sequence()

    metadata_guesser = MetadataGuesser("Dune", None, "Dune", "english")
    assert Status.SUCCESS == metadata_guesser.guess_missing_data()
    assert "Dune, Book 1" == metadata_guesser.get_subtitle()
    assert 1 == metadata_guesser.get_series_sequence()

    metadata_guesser = MetadataGuesser("Dunes", None, "Dune")
    assert Status.ERROR == metadata_guesser.guess_missing_data()

def test_series_name_missing():
    metadata_guesser = MetadataGuesser("Foundation", "The Foundation Trilogy, Book 1", None)
    assert Status.SUCCESS == metadata_guesser.guess_missing_data()
    assert 1 == metadata_guesser.get_series_sequence()
    assert "The Foundation Trilogy" == metadata_guesser.get_series_name()

    metadata_guesser = MetadataGuesser("Foundation", "The Foundation Trilogy, Book 22", None)
    assert Status.SUCCESS == metadata_guesser.guess_missing_data()
    assert 22 == metadata_guesser.get_series_sequence()
    assert "The Foundation Trilogy" == metadata_guesser.get_series_name()

    metadata_guesser = MetadataGuesser("Foundation", "The Foundation Trilogy, 2", None)
    assert Status.SUCCESS == metadata_guesser.guess_missing_data()
    assert 2 == metadata_guesser.get_series_sequence()
    assert "The Foundation Trilogy" == metadata_guesser.get_series_name()

    metadata_guesser = MetadataGuesser("Foundation", "The Foundation Trilogy 2", None)
    assert Status.SUCCESS == metadata_guesser.guess_missing_data()
    assert 2 == metadata_guesser.get_series_sequence()
    assert "The Foundation Trilogy" == metadata_guesser.get_series_name()

    metadata_guesser = MetadataGuesser("Foundation", "22 The Foundation Trilogy", None)
    assert Status.SUCCESS == metadata_guesser.guess_missing_data()
    assert 22 == metadata_guesser.get_series_sequence()
    assert "The Foundation Trilogy" == metadata_guesser.get_series_name()
