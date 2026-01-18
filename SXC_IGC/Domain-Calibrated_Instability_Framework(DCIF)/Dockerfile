FROM python:3.10-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY SXC_CORE_V10_ADAPTIVE.py .
CMD ["python", "SXC_CORE_V10_ADAPTIVE.py"]
