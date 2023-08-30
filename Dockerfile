FROM python:3.8-slim

# Keeps Python from generating .pyc files in the container
ENV PYTHONDONTWRITEBYTECODE=1

# Turns off buffering for easier container logging
ENV PYTHONUNBUFFERED=1

# Install python requirements
COPY requirements.txt .
RUN python -m pip install -r requirements.txt

# Install requirements needed by QT
RUN apt-get update && apt-get install '^libxcb.*-dev' libx11-xcb-dev libglu1-mesa-dev libxrender-dev libxi-dev libxkbcommon-dev libxkbcommon-x11-dev ffmpeg libsm6 libxext6 -y

# Copy needed files to run application
WORKDIR /app
COPY main.py run.sh config.json .
COPY src ./src

# Uncomment for debugging QT issues
# ENV QT_DEBUG_PLUGINS=1

RUN chmod +x ./run.sh
ENTRYPOINT ["/app/run.sh"]
CMD ["config.json"]
