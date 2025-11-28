

def filter_non_ascii(input_string):
    """
    Filters out non-ASCII characters from a given string.
    """
    return "".join(char for char in input_string if ord(char) < 128)
