FROM python:3.9-slim
WORKDIR /app
RUN mkdir output  # Add this line
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY . .
CMD ["python", "app.py"]