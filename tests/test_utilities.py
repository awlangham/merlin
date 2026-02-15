import pytest
from merlin.cli.utilities import _comma_separated_to_ints, _comma_separated_to_strings, _comma_separated_to_floats, _parse_transition


@pytest.mark.parametrize(
    "input_string, expected",
    [
        ("1,2,3", [1, 2, 3]),
        (" 1, 2 ,3 ", [1, 2, 3]),
        ("42", [42]),
        ("0,-1,5", [0, -1, 5]),
    ],
)
def test_valid_inputs(input_string, expected):
    assert _comma_separated_to_ints(input_string) == expected


@pytest.mark.parametrize(
    "bad_input",
    [
        "",
        "1,,2",
        "1,two,3",
        "abc",
    ],
)
def test_invalid_inputs_raise(bad_input):
    with pytest.raises(ValueError):
        _comma_separated_to_ints(bad_input)


@pytest.mark.parametrize(
    "input_string, expected",
    [
        ("a,b,c", ["a", "b", "c"]),
        (" a , b ,c ", ["a", "b", "c"]),
        ("single", ["single"]),
        (" a , b , ", ["a", "b", ""]),
    ],
)
def test_comma_separated_to_strings(input_string, expected):
    assert _comma_separated_to_strings(input_string) == expected


@pytest.mark.parametrize(
    "input_string, expected",
    [
        ("1.0,2.5,3", [1.0, 2.5, 3.0]),
        (" 1 , 2.1 ,3.0 ", [1.0, 2.1, 3.0]),
        ("42", [42.0]),
        ("0,-1.2,5", [0.0, -1.2, 5.0]),
    ],
)
def test_comma_separated_to_floats_valid(input_string, expected):
    assert _comma_separated_to_floats(input_string) == expected


@pytest.mark.parametrize(
    "input_string, expected",
    [
        ("load1::A->B", ("load1", "A", "B")),
        ("loadX::state1->state2", ("loadX", "state1", "state2")),
    ],
)
def test_parse_transition_valid(input_string, expected):
    assert _parse_transition(input_string) == expected


@pytest.mark.parametrize(
    "bad_input", ["", "load1:A->B", "load1::A-B", "load1::A->", "::A->B", "load1::->B"]
)
def test_parse_transition_invalid(bad_input):
    with pytest.raises(ValueError):
        _parse_transition(bad_input)
