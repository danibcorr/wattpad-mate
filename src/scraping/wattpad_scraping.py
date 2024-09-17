import os
import requests
import json
import time
import re

import pandas as pd
import numpy as np
from bs4 import BeautifulSoup
from names_dataset import NameDataset, NameWrapper
from IPython.display import display, HTML
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from loguru import logger


# Load the names dataset
nd = NameDataset()

# Set the user-agent header to avoid 403 Forbidden errors
mozillaheader = {"User-Agent": "Mozilla/5.0"}


def clean_names(names: list[str]) -> list[str]:
    """
    Clean names by removing non-alphanumeric characters and adding spaces before uppercase letters.

    Args:
        names (list): List of names to clean

    Returns:
        list: List of cleaned names
    """

    logger.info("Cleaning names...")

    cleaned_names = []

    for name in names:
        # Remove non-alphanumeric characters
        name = re.sub(r"[^\w\s]", "", name)

        # Add space before an upper case letter before a preceding letter
        name = re.sub(
            r"(?<=[a-z])(?=[A-Z])|(?<=[A-Za-z])(?=[^\w\s])|(?<=[^\w\s])(?=[A-Za-z])",
            "",
            name,
        )

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

    logger.info("Obtaining the gender from the user name...")

    gender_list = []

    for name in name_list:
        first_name = name.split(" ")[0]
        gender_list.append(NameWrapper(nd.search(name=first_name)).gender)

    return gender_list


def convert_to_number(string: str) -> float:
    """
    Convert a string to a number, handling 'K' suffix for thousands.

    Args:
        string (str): String to convert

    Returns:
        float: Converted number
    """

    if "K" in string:
        return float(string.replace("K", "")) * 1000
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


def get_user_info(
    dataset: pd.DataFrame, url_base: str = "https://www.wattpad.com/user/"
) -> None:
    """
    Get user information from Wattpad profiles.

    Args:
        dataset (pandas dataframe): Dataframe with user names
        url_base (str): Base URL for user profiles

    Returns:
        None
    """

    logger.info("Obtaining user information...")

    followers_list = []
    links_list = []
    works_list = []

    for index in dataset.index.values:
        url_user = url_base + dataset.loc[index, "Name"]
        links_list.append(url_user)
        user_info = requests.get(url_user, headers=mozillaheader)
        soup_user_info = BeautifulSoup(user_info.text, "html.parser")
        followers = soup_user_info.findAll(attrs={"class": "followers-count"})
        followers = [convert_to_number(follower.text) for follower in followers]
        works = soup_user_info.find(attrs={"data-id": "profile-works"})
        p = works.find("p")
        works = int(p.text)
        followers_list.append(np.array(followers).astype("int32"))
        works_list.append(np.array(works).astype("int32"))

    dataset["Works"] = works_list
    dataset["Followers"] = np.concatenate(followers_list)
    dataset["Links"] = links_list


def get_usernames(authors: list[str]) -> list[str]:
    """
    Extract usernames from author links.

    Args:
        authors (list): List of author links

    Returns:
        list: List of usernames
    """

    logger.info("Extracting usernames from author links...")

    usernames = []

    for autor in authors:
        # Get the value of the 'href' attribute
        href = autor.get("href")

        # Make sure the 'href' is a user link
        if href.startswith("/user/"):
            # Extract the user name
            username = href.split("/user/")[1]
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

    try:
        options = Options()
        # Run Chrome in headless mode
        options.add_argument("--headless=new")
        # Bypass OS security model
        options.add_argument("--no-sandbox")

        # Initialize the browser driver (in this case, Chrome)
        chrome_service = Service()

        driver = webdriver.Chrome(service=chrome_service, options=options)

        # Opens the web page
        driver.get(urls)

    except Exception as e:
        logger.critical(f"The browser driver could not be loaded: {str(e)}")
        return {}

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
        soup = BeautifulSoup(driver.page_source, "html.parser")

        # We extract the authors' information
        authors = soup.findAll(attrs={"class": "username meta on-navigate"})

        # If we have reached the desired number of users, we exit the loop
        if len(authors) >= limit_users:
            break

        # Calculate the new scroll height and compare it with the last scroll height
        new_height = driver.execute_script("return document.body.scrollHeight")

        if new_height == last_height:
            break

        last_height = new_height

    # Now you can do the scraping to the page with BeautifulSoup
    soup = BeautifulSoup(driver.page_source, "html.parser")

    # We get the information of the authors, number of profile views and votes
    authors = soup.findAll(attrs={"class": "username meta on-navigate"})
    num_visits = soup.findAll(attrs={"class": "read-count"})
    num_votes = soup.findAll(attrs={"class": "vote-count"})

    # Get the names of the users in text format
    usernames = get_usernames(authors)

    # Get the aliases of the users
    aliases = [author.text.split("by ")[1:] for author in authors]
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
        "Name": usernames,
        "Gender": genders,
        "Visits": num_visits,
        "Votes": num_votes,
    }

    # Don't forget to close the driver at the end
    driver.quit()

    return dictionary
