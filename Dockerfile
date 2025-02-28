FROM demisto/python3:3.12.8.1983910

WORKDIR /app

COPY . /app

RUN pip install --no-cache-dir -r requirements.txt

CMD ["python", "main.py"]