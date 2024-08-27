# Uses an official Python image as a basis
FROM python:3-slim

# Create and set the working directory
WORKDIR /home/wattpad_mate

# Install necessary packages and Google Chrome
RUN apt-get update && apt-get install -y \
    wget \
    apt-transport-https \
    gnupg \
    unzip \
    && wget -q -O - https://dl-ssl.google.com/linux/linux_signing_key.pub | gpg --dearmor -o /usr/share/keyrings/google-linux-keyring.gpg \
    && sh -c 'echo "deb [arch=amd64 signed-by=/usr/share/keyrings/google-linux-keyring.gpg] http://dl.google.com/linux/chrome/deb/ stable main" > /etc/apt/sources.list.d/google-chrome.list' \
    && apt-get update && apt-get install -y google-chrome-stable \
    && rm -rf /var/lib/apt/lists/*

# Copy dependency files first to leverage Docker cache
COPY ./pyproject.toml ./poetry.lock ./

# Install the required dependencies
RUN pip install --no-cache-dir poetry \
    && poetry install --no-root \
    && rm -rf /root/.cache/pip

# Copy the rest of the application files
COPY ./src ./src
COPY ./images ./images

# Expose the port to be used by the application
EXPOSE 8501

# Command to start the application
CMD ["poetry", "run", "streamlit", "run", "./src/main.py"]