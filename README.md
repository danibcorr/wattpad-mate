**📚 Wattpad Mate**
================

<p align="center">
  <img src="images/banner.png" alt="Descripción de la imagen" width="600" />
</p>

A web scraping tool to extract user information from Wattpad pages and to be able to meet users with the same tastes and who are accessible to interact with them.

**📋 Description**
---------------

Wattpad Mate is a Streamlit app that allows you to scrape user information from Wattpad pages, filter the results by visits and votes, and display the data in a pandas dataframe. The app uses the `requests`, `BeautifulSoup`, and `Selenium` libraries to scrape the data, and the `Streamlit` library to create a user-friendly interface.

**🧩 Features**
------------

* Scrape user information from Wattpad pages
* Filter results by visits and votes
* Display data in a pandas dataframe
* Get user followers and profile links
* Clean and preprocess user names and aliases
* Determine user gender from names

**🕹️ Usage**
---------

1. Clone the repository and install the required libraries using `pip install -r requirements.txt`.
2. Run the app using `streamlit run web_scraping/wattpad_scraping.py`.
3. Enter the URL of the Wattpad page you want to scrape, and set the minimum and maximum visits and votes filters.
4. Click the "Start Scraping" button to start the scraping process.
5. The app will display the filtered data in a pandas dataframe.

**⚠️ Note**
------

This app is intended for educational purposes only and should not be used to scrape data from Wattpad without explicit permission from Wattpad. I disclaim any responsibility for misuse of this app or any consequences that may arise from unauthorized data scraping from Wattpad. Please respect Wattpad's terms of service and refrain from using this app for any purpose that may violate their policies.