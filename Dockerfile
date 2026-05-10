FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install -r requirements.txt

COPY bot.py .

EXPOSE 6000

CMD ["python", "bot.py"]
