# Use a lightweight Python version
FROM python:3.9-slim

# Set the working directory in the container
WORKDIR /app

# Copy all files from your repo into the container
COPY . .

# Install the required libraries
RUN pip install --no-cache-dir -r requirements.txt

# Expose the port Streamlit runs on
EXPOSE 8000

# Run the application (Ensure your main file is named app.py)
CMD ["streamlit", "run", "app.py", "--server.port=8501", "--server.address=0.0.0.0"]
