# FROM python:3.8-buster

# WORKDIR /raffle_app

# LABEL description="A raffle webapp"

# ENV PYTHONUNBUFFERED=1
# ENV PYTHONDONTWRITEBYTECODE=1

# # RUN apt-get update \
# #     && apt-get -y install libpq-dev gcc

# RUN pip3 install --upgrade pip

# COPY ./requirements.txt /raffle_app/requirements.txt

# RUN pip install -r requirements.txt

# COPY . .

# COPY ./docker/local/django/entrypoint /entrypoint
# RUN sed -i 's/\r$//g' /entrypoint
# RUN chmod +x /entrypoint

# COPY ./docker/local/django/start /start
# RUN sed -i 's/\r$//g' /start
# RUN chmod +x /start

# COPY ./docker/local/django/celery/worker/start /start-celeryworker
# RUN sed -i 's/\r$//g' /start-celeryworker
# RUN chmod +x /start-celeryworker

# COPY ./docker/local/django/celery/beat/start /start-celerybeat
# RUN sed -i 's/\r$//g' /start-celerybeat
# RUN chmod +x /start-celerybeat

# COPY ./docker/local/django/celery/flower/start /start-flower
# RUN sed -i 's/\r$//g' /start-flower
# RUN chmod +x /start-flower

# ENTRYPOINT [ "/entrypoint" ]


# Stage 1: Build Python environment
FROM python:3.9-slim AS builder

RUN apt-get update \
    && apt-get install -y --no-install-recommends \
        build-essential \
        libpq-dev

WORKDIR /raffle_app

# Install dependencies
COPY ./requirements.txt /raffle_app/requirements.txt
RUN pip install --user -r requirements.txt

# Stage 2: Copy app code and configure runtime environment
FROM python:3.9-slim AS runtime

# Install runtime dependencies
RUN apt-get update \
    && apt-get install -y --no-install-recommends \
        libpq5

WORKDIR /raffle_app

# Copy installed Python dependencies from builder stage
COPY --from=builder /root/.local /root/.local

# Set environment variables
ENV PATH=/root/.local/bin:$PATH \
    PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1

# Copy Django app code
COPY . .

COPY ./docker/local/django/entrypoint /entrypoint
RUN sed -i 's/\r$//g' /entrypoint
RUN chmod +x /entrypoint

COPY ./docker/local/django/start /start
RUN sed -i 's/\r$//g' /start
RUN chmod +x /start

COPY ./docker/local/django/celery/worker/start /start-celeryworker
RUN sed -i 's/\r$//g' /start-celeryworker
RUN chmod +x /start-celeryworker

COPY ./docker/local/django/celery/beat/start /start-celerybeat
RUN sed -i 's/\r$//g' /start-celerybeat
RUN chmod +x /start-celerybeat

COPY ./docker/local/django/celery/flower/start /start-flower
RUN sed -i 's/\r$//g' /start-flower
RUN chmod +x /start-flower

ENTRYPOINT [ "/entrypoint" ]
