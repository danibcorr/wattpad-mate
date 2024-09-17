from wattpad_scraping import (
    clean_names,
    convert_to_number,
    make_clickable,
    get_usernames,
)


def test_clean_names():
    """
    Test the clean_names function.

    This function should remove any non-alphanumeric characters from the names.
    """
    assert clean_names(["JohnDoe", "JaneDoe!"]) == ["JohnDoe", "JaneDoe"]


def test_convert_to_number():
    """
    Test the convert_to_number function.

    This function should convert string representations of numbers (including abbreviations) to integers.
    """
    assert convert_to_number("1K") == 1000
    assert convert_to_number("250") == 250


def test_make_clickable():
    """
    Test the make_clickable function.

    This function should wrap a given URL in an HTML anchor tag.
    """
    url = "http://example.com"
    assert make_clickable(url) == f'<a href="{url}">{url}</a>'


def test_get_usernames():
    """
    Test the get_usernames function.

    This function should extract usernames from a list of HTML elements containing user profile links.
    """

    # Mock HTML elements
    class MockElement:
        def __init__(self, href):
            self.href = href

        def get(self, attr):
            if attr == "href":
                return self.href

    # Create a list of mock elements
    elements = [MockElement("/user/johndoe"), MockElement("/user/janedoe")]

    # Test the function
    assert get_usernames(elements) == ["johndoe", "janedoe"]
