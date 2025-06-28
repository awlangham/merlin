def _comma_separated_to_ints(string) -> list[int]:
    return [int(substring.strip()) for substring in string.split(',')]


def _comma_separated_to_strings(string) -> list[str]:
    return [substring.strip() for substring in string.split(',')]


def _comma_separated_to_floats(string) -> list[int]:
    return [float(substring.strip()) for substring in string.split(',')]


def _parse_transition(string) -> tuple[str, str, str]:
    substrings = string.split('::')
    load_name = substrings[0]

    substrings = substrings[1].split('->')
    state1 = substrings[0]
    state2 = substrings[1]

    return load_name, state1, state2
