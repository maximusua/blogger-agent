FROM python:3.11-slim

WORKDIR /app

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy project files
COPY . .

# The environment variables will be passed at runtime
CMD ["python", "test_kyiv_blog.py"] 