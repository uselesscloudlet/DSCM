FROM python:3.10
WORKDIR /src
COPY requirements.txt .
RUN python3 -m pip install -r requirements.txt --no-cache-dir
COPY server.py .

CMD ["uvicorn", "server:app", "--host", "0.0.0.0", "--port", "80"]