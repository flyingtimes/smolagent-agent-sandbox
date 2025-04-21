FROM library/python

# Install build dependencies
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir smolagents[openai] gradio_client pandas openpyxl && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /app

# Run with limited privileges
USER nobody

# Default command
CMD ["python", "-c", "print('Container ready')"]