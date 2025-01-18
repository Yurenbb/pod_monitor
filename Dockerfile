FROM python:3.9-slim
WORKDIR /app
COPY ./test.py .
COPY ./url.txt .
RUN pip install --no-cache-dir kubernetes requests
CMD ["python", "test.py"]
