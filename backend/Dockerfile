FROM python:3.7-slim
WORKDIR /app
COPY . .
RUN apt update && apt install libpq-dev python3-dev gcc -y && rm -rf /var/lib/apt/lists/*
RUN pip3 install -r requirements.txt --no-cache-dir
CMD ["gunicorn", "backend.wsgi:application", "--bind", "0:8000" ]