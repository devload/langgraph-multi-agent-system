FROM python:3.11-slim

WORKDIR /app

# Install Gemini CLI (placeholder - actual installation depends on your setup)
# RUN curl -fsSL https://gemini-cli-install.sh | sh

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

CMD ["uvicorn", "run_gemini:app", "--host", "0.0.0.0", "--port", "8002"]