####################################################
FROM python:3 as production_image

ENV SERVER_IP="0.0.0.0"
ENV SERVER_PORT="8080"
ENV OUTPUT_DIR="/usr/src/app-receiver/output"
ENV DECRYPTION_KEY="/run/secrets/decryption_key"

EXPOSE 8080

# SOME
# DOCKERFILE DIRECTIVES
# ARE MISSING

COPY Pipfile ./
COPY Pipfile.lock ./

RUN mkdir -p /usr/src/app-receiver/output
RUN pip install --no-cache-dir pipenv
RUN pipenv install --system --deploy --ignore-pipfile

ENTRYPOINT ["gunicorn", "server:app"]

# MULTI-STAGE BUILDS
# CAN BE ENABLED
# FOR THIS DOCKER IMAGE