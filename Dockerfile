FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

COPY shared ./shared
COPY api_router.py auth.py consumer.py event_bus.py location_store.py main.py models.py pii_policy.py runtime_secrets.py utils.py ./

EXPOSE 8000

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
