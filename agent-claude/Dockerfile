FROM python:3.11-slim

WORKDIR /app

# Install Claude CLI (placeholder - actual installation depends on your setup)
# RUN curl -fsSL https://claude-cli-install.sh | sh

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

CMD ["uvicorn", "run_claude:app", "--host", "0.0.0.0", "--port", "8001"]