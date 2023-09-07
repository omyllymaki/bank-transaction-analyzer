# Image to run app

FROM ossimyllymaki/bank-transaction-analyzer

# Keeps Python from generating .pyc files in the container
ENV PYTHONDONTWRITEBYTECODE=1

# Turns off buffering for easier container logging
ENV PYTHONUNBUFFERED=1

# Copy needed files to run application
WORKDIR /app
COPY main.py run.sh config.json .
COPY src ./src

# Uncomment for debugging QT issues
# ENV QT_DEBUG_PLUGINS=1

RUN chmod +x ./run.sh
ENTRYPOINT ["/app/run.sh"]
CMD ["config.json"]
