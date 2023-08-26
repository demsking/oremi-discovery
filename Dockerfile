FROM python:3.10-alpine

RUN addgroup -g 1000 oremi \
  && adduser -D -u 1000 -G oremi oremi

USER oremi
ENV PYTHONPATH="~/.local/lib/python3.10/site-packages"
WORKDIR /oremi
COPY pyproject.toml LICENSE build/requirements.txt /oremi/
RUN pip install --no-cache-dir -r requirements.txt
COPY oremi_discovery /oremi/oremi_discovery

ENTRYPOINT ["python", "-m", "oremi_discovery", "--host", "0.0.0.0", "--port", "5105"]

# Adding metadata at the end due to their values being subject to change a each build.
ARG CREATED_DATE
ARG PACKAGE_NAME
ARG MAINTAINER
ARG DESCRIPTION
ARG VERSION
ARG SOURCE_URL
ARG VENDOR
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
LABEL org.opencontainers.image.vendor="$VENDOR"
LABEL org.opencontainers.image.licenses="$LICENSE"
