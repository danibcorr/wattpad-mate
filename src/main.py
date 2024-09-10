import streamlit as st
import pandas as pd
import numpy as np
from loguru import logger

from scraping.wattpad_scraping import scrape_page, get_user_info, make_clickable


# Log storage file
logger.add("./src/logs/app.log", rotation="1 MB", compression="zip")

# Create a Streamlit app
st.set_page_config(page_title="Wattpad Mate", page_icon="📚", layout="wide")

with st.columns(1)[0]:

    st.markdown("<center><h1>Wattpad Mate</h1></center>", unsafe_allow_html=True)

# Create three columns
col1, col2 = st.columns(2)

with col1:

    st.image("./images/banner.png", use_column_width=True)


def main() -> None:
    """
    Main function to scrape user information and filter by visits and votes.
    """

    # Add input fields in the middle column
    with col1:

        url_input = st.text_input(
            "Enter URL:",
            value="https://www.wattpad.com/stories/juvenil%2cnovelajuvenil/new?prev=novelajuvenil",
        )
        min_visits_input = st.number_input("Minimum visits:", value=10, min_value=0)
        max_visits_input = st.number_input("Maximum visits:", value=100000, min_value=0)
        min_votes_input = st.number_input("Minimum votes:", value=10, min_value=0)
        max_votes_input = st.number_input("Maximum votes:", value=500, min_value=0)
        limit_users_input = st.number_input("User limit:", value=20, min_value=1)

        state_button = st.button("Start Scraping")

        if state_button:

            # Scraping the page
            dictionary = scrape_page(url_input, limit_users_input)

            # Find the maximum length of lists in dictionary
            max_len = max(len(lst) for lst in dictionary.values())

            # Make all lists in dictionary the same length
            for key, value in dictionary.items():

                if len(value) < max_len:

                    if len(value) == 0:

                        dictionary[key] = [np.nan] * max_len

                    else:

                        dictionary[key] = value + [np.nan] * (max_len - len(value))

            # Creation of the pandas dataframe
            data = pd.DataFrame(dictionary)

            # We filter the data with the visit and vote conditions
            data_show = data[
                (data["Visits"] >= min_visits_input)
                & (data["Visits"] <= max_visits_input)
                & (data["Votes"] >= min_votes_input)
                & (data["Votes"] <= max_votes_input)
            ]

            # Sort the rows using the Visits column from highest to lowest
            data_show = data_show.sort_values(by=["Visits"], ascending=False)

            # Replace the gender callsign
            data_show["Gender"] = data_show["Gender"].replace("Male", "M")
            data_show["Gender"] = data_show["Gender"].replace("Female", "F")
            data_show["Gender"] = data_show["Gender"].replace("", "-")

            # We make a request for all filtered users and get their followers
            get_user_info(data_show)

            # Show the result
            data_show["Links"] = data_show["Links"].apply(make_clickable)

    if state_button:

        with col2:

            # Display the result in the second column
            st.markdown(
                f"<center>{data_show.to_html(escape=False)}</center>",
                unsafe_allow_html=True,
            )


if __name__ == "__main__":

    # Data collection and visualization
    main()
