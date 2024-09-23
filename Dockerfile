FROM python:3.11.4-slim-bullseye as install-browser

RUN apt-get update \
    && apt-get satisfy -y \
    "chromium, chromium-driver (>= 115.0)" \
    && chromium --version && chromedriver --version

RUN apt-get update \
    && apt-get install -y --fix-missing firefox-esr wget \
    && wget https://github.com/mozilla/geckodriver/releases/download/v0.33.0/geckodriver-v0.33.0-linux64.tar.gz \
    && tar -xvzf geckodriver* \
    && chmod +x geckodriver \
    && mv geckodriver /usr/local/bin/

# Install build tools
RUN apt-get update \
    && apt-get install -y --no-install-recommends \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

FROM install-browser as online-search-gpt-install

ENV PIP_ROOT_USER_ACTION=ignore

RUN mkdir /usr/src/app
WORKDIR /usr/src/app

COPY ./requirements.txt ./requirements.txt
RUN pip install -r requirements.txt

FROM online-search-gpt-install AS online-search-gpt

RUN useradd -ms /bin/bash online-search-gpt \
    && chown -R online-search-gpt:online-search-gpt /usr/src/app

USER online-search-gpt

COPY --chown=online-search-gpt:online-search-gpt ./ ./

EXPOSE 8000
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]