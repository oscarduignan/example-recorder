ARG DOCKERHUB=dockerhub.tax.service.gov.uk
FROM ${DOCKERHUB}/selenium/standalone-chrome:103.0-20220706

USER root

RUN apt-get update -yq

RUN apt-get install curl gnupg python3-pip -yq

RUN curl -sL https://deb.nodesource.com/setup_18.x | bash \
   && apt-get install nodejs -yq

RUN pip install mitmproxy python-ulid

RUN npm install -g @axe-core/cli

RUN curl -o /vnu.jar.zip -sL https://github.com/validator/validator/releases/download/20.6.30/vnu.jar_20.6.30.zip \
   && unzip -j /vnu.jar.zip -d / \
   && rm /vnu.jar.zip

RUN apt-get install rinetd=0.62* -yq

COPY example-recorder /example-recorder

WORKDIR /example-recorder

EXPOSE 8080

CMD ["./record-examples"]
