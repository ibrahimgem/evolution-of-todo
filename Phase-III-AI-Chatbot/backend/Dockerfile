FROM python:3.11-slim

# Install system dependencies (including build tools for bcrypt)
RUN apt-get update && apt-get install -y \
    gcc \
    libpq-dev \
    libffi-dev \
    cargo \
    rustc \
    && rm -rf /var/lib/apt/lists/*

# Create a non-root user for HuggingFace Spaces
RUN useradd -m -u 1000 user

# Set up app directory with correct permissions
WORKDIR /home/user/app
COPY --chown=user:user requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code with correct ownership
COPY --chown=user:user . .

# Switch to non-root user
USER user

# Set environment variables
ENV HOME=/home/user \
    PATH=/home/user/.local/bin:$PATH \
    PYTHONUNBUFFERED=1 \
    DATABASE_URL=sqlite+aiosqlite:////tmp/todos.db

# Expose port 7860 (HuggingFace Spaces default)
EXPOSE 7860

# Run the application
CMD ["python", "-m", "uvicorn", "src.main:app", "--host", "0.0.0.0", "--port", "7860"]
