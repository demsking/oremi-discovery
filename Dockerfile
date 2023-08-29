FROM python:3.10-alpine

ARG CREATED_DATE
ARG PACKAGE_NAME
ARG MAINTAINER
ARG DOCUMENTATION
ARG DESCRIPTION
ARG VERSION
ARG SOURCE_URL
ARG LICENSE
ARG REVISION

# @see https://github.com/opencontainers/image-spec/blob/main/annotations.md
LABEL org.opencontainers.image.title="$PACKAGE_NAME"
LABEL org.opencontainers.image.description="$DESCRIPTION"
LABEL org.opencontainers.image.version="$VERSION"
LABEL org.opencontainers.image.revision="$REVISION"
LABEL org.opencontainers.image.authors="$MAINTAINER"
LABEL org.opencontainers.image.created="$CREATED_DATE"
LABEL org.opencontainers.image.source="$SOURCE_URL"
LABEL org.opencontainers.image.url="$SOURCE_URL"
LABEL org.opencontainers.image.documentation="$SOURCE_URL#readme"
LABEL org.opencontainers.image.licenses="$LICENSE"
LABEL maintainer="$MAINTAINER"

RUN addgroup -g 1000 oremi \
  && adduser -D -u 1000 -G oremi oremi \
  && pip install --no-cache-dir --upgrade pip

COPY pyproject.toml LICENSE build/requirements.txt /oremi/
COPY discovery /oremi/discovery

USER oremi
ENV PATH="/home/oremi/.local/bin:$PATH"
ENV PYTHONPATH="/oremi:$PYTHONPATH"
RUN pip install --no-cache-dir -r /oremi/requirements.txt
ENTRYPOINT ["python", "-m", "discovery", "--host", "0.0.0.0", "--port", "5105"]
