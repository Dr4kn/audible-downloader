import re

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
    p = '[\d]+([.,][\d]+)?'
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
def parse_roman_numberal(numeral):
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
            return 0
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

def get_series_sequence(title: str, subtitle: str, series_name: str) -> None | int:
    if subtitle is not None and series_name is not None:
        matching_words = return_perfect_match(subtitle, series_name)
        if len(matching_words) == 0:
            return None
        no_series_sequence = subtitle.replace(matching_words, "")
        # if the subtitle perfectly matches with the series it is very probably the first book in it
        if len(no_series_sequence) == 0:
            return 1
        numbers_found = get_numbers_from_string(no_series_sequence)
        if len(numbers_found) == 1:
                return numbers_found[0]
        elif len(numbers_found) == 0:
            removed_symbols = re.sub(r',|\.|\(|\)|:|\[|\]|\{|\}', ' ', no_series_sequence)
            numbers = [parse_roman_numberal(number) for number in removed_symbols.split()]
            only_correctly_parsed_numbers = [number for number in numbers if number != 0]
            if len(only_correctly_parsed_numbers) == 1:
                return only_correctly_parsed_numbers[0]