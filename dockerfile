FROM python:3.11.8-slim-bullseye as builder

# setting workdir for builder
WORKDIR /app

# update apt and install gcc to build python packages with C extension
RUN --mount=type=cache,target=/var/cache/apt,sharing=locked \
    --mount=type=cache,target=/var/lib/apt,sharing=locked \
    apt-get update && apt-get install -y --no-install-recommends gcc

# copy folder with requirement files
COPY /requirements ./requirements

# download and build .whl files to use it later 
RUN --mount=type=cache,target=~/.cache/pip \
    pip3 wheel --wheel-dir /app/wheels \ 
    -r requirements/production.txt


FROM python:3.11.8-slim-bullseye as production

ENV PYTHONDONTWRITEBYTECODE 1 \
    PYTHONUNBUFFERED 1
ARG APP_DIR=/app
ARG APP_USER="django_user"

WORKDIR $APP_DIR

# copy wheel and requirement files from builder stage
COPY --from=builder /app/wheels ./wheels
COPY --from=builder /app/requirements/ .

# install pre-compiled packages
RUN pip3 install --no-cache ./wheels/*

# copy application files
COPY . .

RUN useradd -r -s /bin/false $APP_USER && \
    chown -R $APP_USER:$APP_USER $APP_DIR && \
    mkdir -p /vol/web/ && chmod 755 -R /vol/web && \
    mv ./vol/web/* /vol/web/ && \
    python3 manage.py collectstatic --noinput 


USER $APP_USER
# expose image port
EXPOSE 8000
ENTRYPOINT ["sh", "-c", "./start.sh"]