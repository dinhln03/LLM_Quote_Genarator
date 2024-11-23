FROM python:3.9-slim AS compile-image

# Define virtual env
ENV VIRTUAL_ENV=/opt/venv
RUN python3 -m venv $VIRTUAL_ENV
ENV PATH="$VIRTUAL_ENV/bin:$PATH"
COPY ./requirements.txt .
RUN /opt/venv/bin/pip install -r ./requirements.txt --no-cache-dir

FROM python:3.9-alpine AS runtime-image

LABEL maintainer="dinhln"
LABEL organization="individual"
COPY --from=compile-image /opt/venv /opt/venv
RUN apk upgrade --no-cache && \
    apk add --no-cache libgcc libstdc++ ncurses-libs gcompat 
WORKDIR /app/ 

COPY ./app /app
COPY .env /app/.env

# Set environment variables
ENV PATH="/opt/venv/bin:$PATH"

EXPOSE 30000

CMD /bin/sh -c "set -a && source .env && set +a && uvicorn main:app --host 0.0.0.0 --port 30000"