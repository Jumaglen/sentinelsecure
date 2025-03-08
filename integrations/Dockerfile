FROM python:3.9

WORKDIR /app
COPY . .
RUN pip install --no-cache-dir flask requests

ENTRYPOINT ["python3"]
CMD ["wazuh_alert_parser.py"]  # Default command, but overridden in docker-compose
