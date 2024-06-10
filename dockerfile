FROM python:3
RUN mkdir -p /home/wattpad_mate
WORKDIR /home/wattpad_mate
COPY . /home/wattpad_mate
RUN pip install --no-cache-dir -r requirements.txt
EXPOSE 8501
CMD ["python", "streamlit run ./web_scraping/wattpad_scraping.py"]