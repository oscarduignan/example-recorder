FROM mitmproxy/mitmproxy:latest

WORKDIR /

COPY capture-examples.py /capture-examples.py

RUN pip install python-ulid

CMD mitmdump -s /capture-examples.py

