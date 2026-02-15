def _comma_separated_to_ints(string) -> list[int]:
    return [int(substring.strip()) for substring in string.split(',')]


def _comma_separated_to_strings(string) -> list[str]:
    return [substring.strip() for substring in string.split(',')]


def _comma_separated_to_floats(string) -> list[int]:
    return [float(substring.strip()) for substring in string.split(',')]


def _parse_transition(string) -> tuple[str, str, str]:
    try:
        substrings = string.split('::')
        load_name = substrings[0]

        substrings = substrings[1].split('->')
        state1 = substrings[0]
        state2 = substrings[1]
    except IndexError:
        raise ValueError(f'Invalid transition format: {string}')

    if load_name == "":
        raise ValueError(f'Load name cannot be blank in: {string}')

    if state1 == "" or state2 == "":
        raise ValueError(f'State name cannot be blank in: {string}')

    return load_name, state1, state2
