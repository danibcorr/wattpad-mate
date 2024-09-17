import streamlit as st
from streamlit.testing.v1 import AppTest

from main import main


def test_main():
    """
    Test the main function of the Wattpad scraper.

    This test function uses mock objects to simulate user inputs and the scraping process.
    It checks if the main function correctly calls the scrape_page function with the right parameters.
    """
    at = AppTest.from_file("src/main.py")

    # Simulate text input (URL)
    at.text_input(key="url_input").set_value(
        "https://www.wattpad.com/stories/juvenil%2cnovelajuvenil/new?prev=novelajuvenil"
    ).run()

    # Simulate number inputs (various parameters)
    at.number_input(key="min_visits_input").set_value(10).run()
    at.number_input(key="max_visits_input").set_value(100000).run()
    at.number_input(key="min_votes_input").set_value(10).run()
    at.number_input(key="max_votes_input").set_value(500).run()
    at.number_input(key="limit_users_input").set_value(5).run()

    # Simulate button press
    at.button(key="start_scraping").click().run()

    # Execute the main function
    main()
    assert at.success[0].value == "Successfully obtained data"
