import re
from .helper import Status

def return_perfect_match(string1: str, string2: str) -> str:
    if len(string1) >= len(string2):
        check_against = string1
        string = string2
    else:
        check_against = string2
        string = string1
    current_position = 0
    offset = 0
    while len(check_against) - 1 >= current_position + offset:
        matching_string = ""
        while check_against[current_position + offset] == string[current_position]:
            matching_string += string[current_position]
            current_position += 1
            if len(string) == current_position:
                return matching_string
            if len(check_against) <= current_position + offset:
                return ""
        current_position = 0
        offset += 1
    return ""

# https://stackoverflow.com/questions/4289331/how-to-extract-numbers-from-a-string-in-python
def get_numbers_from_string(string: str) -> list[str]:
    numbers_found = []
    p = '[0-9]+([.,][0-9]+)?'
    if re.search(p, string) is not None:
        for catch in re.finditer(p, string):
            try:
                number = int(catch[0])
            except:
                number = float(catch[0].replace(',', '.'))
            numbers_found.append(number)
    return numbers_found

# https://stackoverflow.com/questions/37372603/how-to-remove-specific-substrings-from-a-set-of-strings-in-python
# returns 0 for incorrect value otherwise returns a number:
def parse_roman_numeral(numeral) -> int | None:
    ROMAN_CONSTANTS = (
                ( "", "I", "II", "III", "IV", "V", "VI", "VII", "VIII", "IX" ),
                ( "", "X", "XX", "XXX", "XL", "L", "LX", "LXX", "LXXX", "XC" ),
                ( "", "C", "CC", "CCC", "CD", "D", "DC", "DCC", "DCCC", "CM" ),
                ( "", "M", "MM", "MMM", "",   "",  "-",  "",    "",     ""   ),
            )

    ROMAN_SYMBOL_MAP = dict(I=1, V=5, X=10, L=50, C=100, D=500, M=1000)
    numeral = numeral.upper()
    result = 0
    lastVal = 0
    lastCount = 0
    subtraction = False
    for symbol in numeral[::-1]:
        value = ROMAN_SYMBOL_MAP.get(symbol)
        if not value:
            return None
        if lastVal == 0:
            lastCount = 1
            lastVal = value
        elif lastVal == value:
            lastCount += 1
            # exceptions
        else:
            result += (-1 if subtraction else 1) * lastVal * lastCount
            subtraction = lastVal > value
            lastCount = 1
            lastVal = value
    return result + (-1 if subtraction else 1) * lastVal * lastCount

def word_to_number(word: str):
    word_number_mapping = {
        'one': 1,
        'two': 2,
        'three': 3,
        'four': 4,
        'five': 5,
        'six': 6,
        'seven': 7,
        'eight': 8,
        'nine': 9,
        'ten': 10,
    }
    return word_number_mapping.get(word.lower())

class MetadataGuesser:
    def __init__(self, title: str, subtitle: str | None, series_name: str | None, language = None):
        self.title = title
        self.subtitle = subtitle
        self.series_name = series_name
        self.series_sequence = None
        self.language = language

    # return: Success or error
    def guess_missing_data(self) -> Status:
        if all((self.subtitle is None, self.series_name is None)):
            return Status.ERROR

        if self.subtitle is None:
            if self.title == self.series_name:
                if self.language == "english":
                    self.subtitle = f"{self.title}, Book 1"
                else:
                    self.subtitle = f"{self.title} 1"
                self.series_sequence = 1
                return Status.SUCCESS
            else:
                return Status.ERROR
        
        if self.series_name is None:
            #TODO check for ,Book number
            p = r"[,;:] *[a-zA-Z]* *[0-9]+ *| *[0-9]+ *"
            results = re.findall(p, self.subtitle)
            if len(results) != 1:
                return Status.ERROR
            self.series_sequence = get_numbers_from_string(results[0])[0]
            self.series_name = self.subtitle.replace(results[0], "")
            return Status.SUCCESS
            
        matching_words = return_perfect_match(self.subtitle, self.series_name)
        if len(matching_words) == 0:
            return Status.ERROR
        no_series_sequence = self.subtitle.replace(matching_words, "")
        # if the subtitle perfectly matches with the series it is very probably the first book in it
        if len(no_series_sequence) == 0:
            self.series_sequence = 1
            return Status.SUCCESS
        numbers_found = get_numbers_from_string(no_series_sequence)
        if len(numbers_found) == 1:
                self.series_sequence = numbers_found[0]
                return Status.SUCCESS
        elif len(numbers_found) == 0:
            removed_symbols = re.sub(r',|\.|\(|\)|:|\[|\]|{|}|;|\||\\|/', ' ', no_series_sequence)
            numbers = []
            for number in removed_symbols.split():
                parsed_number = parse_roman_numeral(number)
                if parsed_number is not None:
                    numbers.append(parsed_number)
                parsed_number = word_to_number(number)
                if parsed_number is not None:
                    numbers.append(parsed_number)
                if len(numbers) > 1:
                    return Status.ERROR
            self.series_sequence = numbers[0]
            return Status.SUCCESS
    
    def get_subtitle(self) -> str:
        return self.subtitle

    def get_series_name(self) -> str:
        return self.series_name

    def get_series_sequence(self) -> int | float:
        return self.series_sequence