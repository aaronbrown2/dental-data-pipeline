FROM python:3.11-slim

#Create a new group and non-root user
RUN groupadd -g 1000 appgroup && \
    useradd -m -u 1000 -g appgroup appuser

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

#Copy all files and assign new non-root user as owner
COPY --chown=appuser:appgroup . .

#Switch to non-root user
USER appuser

EXPOSE 8000

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]