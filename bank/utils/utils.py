from typing import List


def parse_boolean_query_param(param_value: str | None) -> bool | None:
    """
    Parses a string query parameter into a boolean.

    Args:
        param_value (str): The string value to parse.

    Returns:
        Optional[bool]: True, False, or None if no valid conversion or default is found.

    Raises:
        ValueError: If param_value is not None but cannot be parsed as a boolean.
    """
    true_strings = set(["true", "1", "on", "yes"])
    false_strings = set(["false", "0", "off", "no"])

    if param_value is None:
        return False

    lower_value = param_value.lower()

    if lower_value in true_strings:
        return True
    elif lower_value in false_strings:
        return False
    else:
        raise ValueError(
            f"Invalid boolean value '{param_value}'. Expected one of {true_strings | false_strings}."
        )


if __name__ == "__main__":
    print("*** Parsing Function Tests ***")
    print(f"'true' -> {parse_boolean_query_param('true')}")
    print(f"'True' -> {parse_boolean_query_param('True')}")
    print(f"'1' -> {parse_boolean_query_param('1')}")
    print(f"'on' -> {parse_boolean_query_param('on')}")
    print(f"'FALSE' -> {parse_boolean_query_param('FALSE')}")
    print(f"'0' -> {parse_boolean_query_param('0')}")

    try:
        parse_boolean_query_param("yesplease")
    except ValueError as e:
        print(f"Error for 'yesplease': {e}")
