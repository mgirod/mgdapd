####################################################
FROM python:3 as development_image

ENV SERVER_IP="0.0.0.0"
ENV SERVER_PORT="8080"
ENV OUTPUT_DIR="/usr/src/app-receiver/output"
ENV DECRYPTION_KEY="/run/secrets/decryption_key"

EXPOSE 8080

# COPY receiver/gunicorn.conf.py ./
# COPY receiver/server.py ./
# RUN mkdir ./service
# COPY receiver/service ./service/
RUN mkdir -p ./receiver/service
COPY receiver ./receiver
COPY receiver/service ./service/

COPY Pipfile ./
COPY Pipfile.lock ./

RUN mkdir -p /usr/src/app-receiver/output
RUN pip install --no-cache-dir pipenv
RUN pipenv install --system --deploy --ignore-pipfile

RUN pip install pytest
RUN mkdir tests
COPY tests tests/
RUN echo -n 'File is decrypted and saved to /usr/src/app-receiver/output/testfile.xml' > /usr/src/app-receiver/output/testfile.xml
RUN pytest -v tests

FROM development_image as production_image

WORKDIR receiver
ENTRYPOINT ["gunicorn", "server:app"]
