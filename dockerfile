# Uses an official Python image as a basis
FROM python:3

# Create and set the working directory
WORKDIR /home/wattpad_mate

# Install necessary packages and Microsoft Edge
RUN apt-get update && apt-get install -y wget apt-transport-https unzip && \
    wget https://packages.microsoft.com/repos/edge/pool/main/m/microsoft-edge-stable/microsoft-edge-stable_125.0.2535.92-1_amd64.deb -O microsoft-edge.deb && \
    dpkg -i microsoft-edge.deb || apt-get -f install -y && \
    apt-get install -y microsoft-edge-stable

# Copy the files needed to install the dependencies
COPY requirements.txt ./

# Install the required dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the files
COPY ./web_scraping/wattpad_scraping.py .
COPY ./images ./images
COPY ./web_scraping/msedgedriver .

# Expose the port to be used by the application
EXPOSE 8501

# Command to start the application
CMD ["streamlit", "run", "wattpad_scraping.py"]