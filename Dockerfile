##
## Stage 1: Install dependencies
FROM python:3.10-alpine
WORKDIR /src
COPY python/pyproject.toml python/poetry.lock ./

RUN poetry install --no-root --no-dev --no-interaction --no-ansi \
  && export PYTHONPATH=$(realpath /root/.cache/pypoetry/virtualenvs/$PACKAGE_NAME*) \
  && mv $PYTHONPATH ./venv


##
## Stage 2: Create final image
FROM python:3.10-alpine

RUN addgroup -g 1000 oremi \
  && adduser -D -u 1000 -G oremi oremi

COPY python/pyproject.toml LICENSE /oremi/
COPY python/oremi_discovery /oremi/discovery
COPY bin/ /opt/oremi/bin

USER oremi
ENV PATH="/home/oremi/.local/bin:$PATH"
ENV PYTHONPATH="/oremi:$PYTHONPATH"
ENV DISCOVERY_CHANNEL="discovery"
ENV MQTT_PORT="1883"
ENTRYPOINT ["python", "oremi-discovery", "--host", "0.0.0.0", "--port", "5105"]
