FROM python:3.8-slim

# Keeps Python from generating .pyc files in the container
ENV PYTHONDONTWRITEBYTECODE=1

# Turns off buffering for easier container logging
ENV PYTHONUNBUFFERED=1

# Install requirements
COPY requirements.txt .
RUN python -m pip install -r requirements.txt

# These are needed for QT
RUN apt-get update && apt-get install '^libxcb.*-dev' libx11-xcb-dev libglu1-mesa-dev libxrender-dev libxi-dev libxkbcommon-dev libxkbcommon-x11-dev ffmpeg libsm6 libxext6 -y

WORKDIR /app
COPY . /app

# Creates a non-root user with an explicit UID and adds permission to access the /app folder
RUN adduser -u 5678 --disabled-password --gecos "" appuser && chown -R appuser /app
USER appuser

# Uncomment for debugging QT issues
# ENV QT_DEBUG_PLUGINS=1

RUN chmod +x ./run.sh
ENTRYPOINT ["/app/run.sh"]
CMD ["config.json"]
