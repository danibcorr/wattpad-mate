# Uses an official Python image as a basis
FROM python:3-slim

# Create and set the working directory
WORKDIR /home/wattpad_mate

# Install necessary packages and Google Chrome
RUN apt-get update && apt-get install -y wget apt-transport-https gnupg unzip && \
    wget -q -O - https://dl-ssl.google.com/linux/linux_signing_key.pub | apt-key add - && \
    sh -c 'echo "deb [arch=amd64] http://dl.google.com/linux/chrome/deb/ stable main" >> /etc/apt/sources.list.d/google-chrome.list' && \
    apt-get update && apt-get install -y google-chrome-stable && \
    rm -rf /var/lib/apt/lists/*

# Install ChromeDriver
RUN CHROME_DRIVER_VERSION=`wget -qO- https://chromedriver.storage.googleapis.com/LATEST_RELEASE` && \
    wget -O /tmp/chromedriver.zip https://chromedriver.storage.googleapis.com/${CHROME_DRIVER_VERSION}/chromedriver_linux64.zip && \
    unzip /tmp/chromedriver.zip chromedriver -d /usr/local/bin/ && \
    rm /tmp/chromedriver.zip

# Copy the files needed to install the dependencies
COPY requirements.txt ./

# Install the required dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the files
COPY ./web_scraping/ .
COPY ./images ./images

# Expose the port to be used by the application
EXPOSE 8501

# Command to start the application
CMD ["streamlit", "run", "wattpad_scraping.py"]