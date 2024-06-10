# %% Libraries

import streamlit as st
import requests
import json
from bs4 import BeautifulSoup
import pandas as pd
import numpy as np
import time
from names_dataset import NameDataset, NameWrapper
import re
from IPython.display import display, HTML
from selenium import webdriver
from selenium.webdriver.edge.service import Service
from selenium.webdriver.edge.options import Options

# %%  Global variables/parameters

# Create a Streamlit app
st.set_page_config(page_title = "Wattpad Mate", page_icon = "📚", layout = "wide")

with st.columns(1)[0]:

    st.markdown("<center><h1>Wattpad Mate</h1></center>", unsafe_allow_html=True)

# Create three columns
col1, col2, col3 = st.columns(3)

with col2:

    st.image("./images/banner.png", width = 560)

# Load the names dataset
nd = NameDataset()

# Set the user-agent header to avoid 403 Forbidden errors
mozillaheader = {"User-Agent": "Mozilla/5.0"}

# %%  Functions

def clean_names(names: list[str]) -> list[str]:

    """
    Clean names by removing non-alphanumeric characters and adding spaces before uppercase letters.
    
    Args:
        names (list): List of names to clean
    
    Returns:
        list: List of cleaned names
    """

    cleaned_names = []

    for name in names:

        # Remove non-alphanumeric characters
        name = re.sub(r'[^\w\s]', '', name)

        # Add space before an upper case letter before a preceding letter
        name = re.sub(r'(?<=[a-z])(?=[A-Z])|(?<=[A-Za-z])(?=[^\w\s])|(?<=[^\w\s])(?=[A-Za-z])','', name)
        
        # Eliminate leading and trailing blanks
        name = name.strip()
        cleaned_names.append(name)

    return cleaned_names

def get_gender_from_name(name_list: list[str]) -> list[str]:

    """
    Get the gender of each name in the list using the NameDataset library.
    
    Args:
        name_list (list): List of names
    
    Returns:
        list: List of genders corresponding to each name
    """

    gender_list = []

    for name in name_list:

        first_name = name.split(' ')[0]
        gender_list.append(NameWrapper(nd.search(name = first_name)).gender)

    return gender_list

def convert_to_number(string: str) -> float:

    """
    Convert a string to a number, handling 'K' suffix for thousands.
    
    Args:
        string (str): String to convert
    
    Returns:
        float: Converted number
    """

    if 'K' in string:

        return float(string.replace('K', '')) * 1000

    else:

        return float(string)

def make_clickable(val: str) -> str:

    """
    Make a URL clickable in a pandas dataframe.
    
    Args:
        val (str): URL to make clickable
    
    Returns:
        str: Clickable URL
    """

    return '<a href="{}">{}</a>'.format(val, val)

def get_user_info(dataset: pd.DataFrame, url_base: str = "https://www.wattpad.com/user/") -> None:

    """
    Get user information from Wattpad profiles.
    
    Args:
        dataset (pandas dataframe): Dataframe with user names
        url_base (str): Base URL for user profiles
    
    Returns:
        None
    """

    followers_list = []
    links_list = []
    works_list = []

    for index in dataset.index.values:

        url_user = url_base + dataset.loc[index, 'Nombre']
        links_list.append(url_user)
        user_info = requests.get(url_user, headers = mozillaheader)
        soup_user_info = BeautifulSoup(user_info.text, "html.parser")
        followers = soup_user_info.findAll(attrs = {"class": "followers-count"})
        followers = [convert_to_number(follower.text) for follower in followers]
        works = soup_user_info.find(attrs = {"data-id": "profile-works"})
        p = works.find('p')
        works = int(p.text)
        followers_list.append(np.array(followers).astype('int32'))
        works_list.append(np.array(works).astype('int32'))

    dataset["Trabajos"] = works_list
    dataset["Seguidores"] = np.concatenate(followers_list)
    dataset["Enlaces"] = links_list
    
def get_usernames(authors: list[str]) -> list[str]:

    """
    Extract usernames from author links.
    
    Args:
        authors (list): List of author links
    
    Returns:
        list: List of usernames
    """

    usernames = []

    for autor in authors:

        # Get the value of the 'href' attribute
        href = autor.get('href')

        # Make sure the 'href' is a user link
        if href.startswith('/user/'):

             # Extract the user name
            username = href.split('/user/')[1]
            usernames.append(username)

    return usernames

def scrape_page(urls: str, limit_users: int = 200) -> dict:

    """
    Scrape user information from a Wattpad page.
    
    Args:
        urls (str): URL of the page to scrape
        limit_users (int): Maximum number of users to scrape
    
    Returns:
        dict: Dictionary with user information
    """

    # Initialize the browser driver (in this case, Edge)
    options = Options()
    options.binary_location = r'./msedgedriver'
    options.add_argument("--headless=new")
    driver = webdriver.Edge(options = options)

    # Opens the web page
    driver.get(urls)

    # Simulates scroll down
    SCROLL_PAUSE_TIME = 2

    # Get scroll height
    last_height = driver.execute_script("return document.body.scrollHeight")

    while True:

        # Scroll down
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")

        # Wait for page to load
        time.sleep(SCROLL_PAUSE_TIME)

        # Now you can do the scraping to the page with BeautifulSoup
        soup = BeautifulSoup(driver.page_source, 'html.parser')

        # We extract the authors' information
        authors = soup.findAll(attrs = {"class": "username meta on-navigate"})

        # If we have reached the desired number of users, we exit the loop
        if len(authors) >= limit_users:

            break

        # Calculate the new scroll height and compare it with the last scroll height
        new_height = driver.execute_script("return document.body.scrollHeight")

        if new_height == last_height:

            break

        last_height = new_height

    # Now you can do the scraping to the page with BeautifulSoup
    soup = BeautifulSoup(driver.page_source, 'html.parser')

    # We get the information of the authors, number of profile views and votes
    authors = soup.findAll(attrs = {"class": "username meta on-navigate"})
    num_visits = soup.findAll(attrs = {"class": "read-count"})
    num_votes = soup.findAll(attrs = {"class": "vote-count"})

    # Get the names of the users in text format
    usernames = get_usernames(authors)

    # Get the aliases of the users
    aliases = [author.text.split('by ')[1:] for author in authors]
    aliases = np.concatenate(aliases)

    # We clean the aliases of the users to remove certain characters and get their possible gender
    clean_alias = clean_names(aliases)
    genders = get_gender_from_name(clean_alias)

    # We get the number of visits of the page book to scrape from the specific user
    num_visits = [visit.text.split('auto"/>')[0] for visit in num_visits]
    num_visits = [convert_to_number(value) for value in num_visits]

    # We get the number of votes in the book of the page to scrape from the specific user
    num_votes = [vote.text.split('auto"/>')[0] for vote in num_votes]
    num_votes = [convert_to_number(value) for value in num_votes]

    # We create a dictionary that gathers all information    
    dictionary = {
        "Alias": aliases,
        "Nombre": usernames,
        "Genero": genders,
        "Visitas": num_visits,
        "Votos": num_votes,
    }

    # Don't forget to close the driver at the end
    driver.quit()

    return dictionary

def main() -> None:

    """
    Main function to scrape user information and filter by visits and votes.
    """

    # Add input fields in the middle column
    with col2:

        url_input = st.text_input("Enter URL:", value = "https://www.wattpad.com/stories/juvenil%2cnovelajuvenil/new?prev=novelajuvenil")
        min_visits_input = st.number_input("Minimum visits:", value = 10, min_value = 0)
        max_visits_input = st.number_input("Maximum visits:", value = 100000, min_value = 0)
        min_votes_input = st.number_input("Minimum votes:", value = 10, min_value = 0)
        max_votes_input = st.number_input("Maximum votes:", value = 500, min_value = 0)
        limit_users_input = st.number_input("User limit:", value = 20, min_value = 1)

        state_button = st.button("Start Scraping")
        
        if state_button:

            # Scraping the page
            dictionary = scrape_page(url_input, limit_users_input)

            # Creation of the pandas dataframe
            data = pd.DataFrame(dictionary)

            # We filter the data with the visit and vote conditions
            data_show = data[(data['Visitas'] >= min_visits_input) & (data['Visitas'] <= max_visits_input) &
                            (data['Votos'] >= min_votes_input) & (data['Votos'] <= max_votes_input)]

            # Sort the rows using the Visits column from highest to lowest
            data_show = data_show.sort_values(by=['Visitas'], ascending=False)

            # Replace the gender callsign
            data_show["Genero"] = data_show["Genero"].replace("Male", "M")
            data_show["Genero"] = data_show["Genero"].replace("Female", "F")
            data_show["Genero"] = data_show["Genero"].replace("", "-")

            # We make a request for all filtered users and get their followers
            get_user_info(data_show)

            # Show the result
            data_show['Enlaces'] = data_show['Enlaces'].apply(make_clickable)

    if state_button:

        # Display the result in the second column
        st.markdown(f'<center>{data_show.to_html(escape=False)}</center>', unsafe_allow_html=True)

# %% Main

if __name__ == '__main__':

    # Data collection and visualization
    main()