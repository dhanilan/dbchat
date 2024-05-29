FROM nikolaik/python-nodejs:python3.12-nodejs20-bullseye

COPY src src

COPY requirements.txt .

RUN python -m pip install --upgrade pip \
    && python -m pip install -r requirements.txt

RUN cd src/ui \
    && npm install

COPY run.sh .

COPY run_client.sh .

COPY run_server.sh .

EXPOSE 8000 5173

CMD ./run.sh
