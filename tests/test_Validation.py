import pytest
from Validation import (
    validate_support_count,
    validate_support_order,
    validate_points,
    validate_float_list,
    validate_udl_count,
    validate_udl_spec,
    validate_support_location,
    validate_uvl_count,
    validate_uvl_spec,
    analyze_input_state,
)


def test_validate_support_count_valid():
    assert validate_support_count("1") == 1
    assert validate_support_count("2") == 2


def test_validate_support_count_invalid():
    with pytest.raises(ValueError, match="Supports must be 1"):
        validate_support_count("3")
    with pytest.raises(ValueError, match="Supports must be 1"):
        validate_support_count("0")


def test_validate_support_order_valid():
    # Should not raise an exception
    validate_support_order(0.0, 10.0)


def test_validate_support_order_invalid():
    with pytest.raises(ValueError, match="must be placed strictly before"):
        validate_support_order(10.0, 0.0)
    with pytest.raises(ValueError, match="must be placed strictly before"):
        validate_support_order(5.0, 5.0)


def test_validate_support_location():
    assert validate_support_location("5.0", 0.0, 10.0, "Support A") == 5.0

    assert validate_support_location("", 2.5, 10.0, "Support A") == 2.5

    with pytest.raises(ValueError, match="must be between 0 and beam length"): validate_support_location("15.0", 0.0, 10.0, "Support A")


def test_validate_points_valid():
    assert validate_points("2.0, 5.0, 8.5", 10.0) == [2.0, 5.0, 8.5]
    assert validate_points("", 10.0) == []


def test_validate_points_out_of_bounds():
    with pytest.raises(ValueError, match="must be between 0 and 10.0m"):
        validate_points("2.0, 12.0", 10.0)
    with pytest.raises(ValueError, match="must be between 0 and 10.0m"):
        validate_points("-1.0, 5.0", 10.0)


def test_validate_float_list_valid():
    assert validate_float_list("10, 20, 30", 3, "Loads") == [10.0, 20.0, 30.0]
    assert validate_float_list("", 2, "Loads") == [0.0, 0.0]


def test_validate_float_list_length_mismatch():
    with pytest.raises(ValueError, match="Length mismatch! Expected 3 values"):
        validate_float_list("10, 20", 3, "Loads")


def test_validate_udl_uvl_counts():
    # UDL Count
    assert validate_udl_count("3") == 3
    assert validate_udl_count("") == 0
    with pytest.raises(ValueError, match="UDL count cannot be negative"):
        validate_udl_count("-1")

    # UVL Count
    assert validate_uvl_count("2") == 2
    assert validate_uvl_count("") == 0
    with pytest.raises(ValueError, match="UVL count cannot be negative"):
        validate_uvl_count("-2")


def test_validate_udl_spec_valid():
    assert validate_udl_spec("0, 5, -10.0", 10.0) == (0.0, 5.0, -10.0)


def test_validate_udl_spec_invalid():
    with pytest.raises(ValueError, match="requires exactly 3 values"):
        validate_udl_spec("0, 5", 10.0)

    with pytest.raises(ValueError, match="Invalid UDL bounds"):
        validate_udl_spec("5, 2, -10.0", 10.0)
    with pytest.raises(ValueError, match="Invalid UDL bounds"):
        validate_udl_spec("0, 15, -10.0", 10.0)


def test_validate_uvl_spec_valid():
    assert validate_uvl_spec("2, 8, -5, -15", 10.0) == (2.0, 8.0, -5.0, -15.0)


def test_validate_uvl_spec_invalid():
    # Wrong length
    with pytest.raises(ValueError, match="requires exactly 4 values"):
        validate_uvl_spec("2, 8, -5", 10.0)

    # Invalid span logic
    with pytest.raises(ValueError, match="Invalid UVL bounds"):
        validate_uvl_spec("8, 2, -5, -15", 10.0)


def test_analyze_input_state_float():
    assert analyze_input_state("", "float") == "empty"
    assert analyze_input_state("-", "float") == "incomplete"
    assert analyze_input_state("e-", "float") == "incomplete"
    assert analyze_input_state("15.5", "float") == "valid"

    assert analyze_input_state("-5.0", "float") == "invalid"
    assert analyze_input_state("abc", "float") == "invalid"


def test_analyze_input_state_float_list():
    assert analyze_input_state("", "float_list") == "empty"
    assert analyze_input_state("10, -, 30", "float_list") == "incomplete"
    assert analyze_input_state("10, 20, 30", "float_list") == "valid"
    assert analyze_input_state("abc, 20", "float_list") == "invalid"


def test_analyze_input_state_udl_list():
    assert analyze_input_state("0, 5, -10", "udl_list") == "valid"
    assert analyze_input_state("0, 5", "udl_list") == "incomplete"
    assert analyze_input_state("0, 5, -10; 5, -, -5", "udl_list") == "incomplete"
    assert analyze_input_state("0, 5, -10, 20", "udl_list") == "invalid"


def test_analyze_input_state_uvl_list():
    assert analyze_input_state("0, 5, -5, -10", "uvl_list") == "valid"
    assert analyze_input_state("0, 5, -5", "uvl_list") == "incomplete"
    assert analyze_input_state("0, 5, -5, -10, 15", "uvl_list") == "invalid"