# DBChat
An agentic AI application for chatting with existing databases

# Features
- Uses an Agentic approach to answer to user's question
- Safe from user executing malicious DDL queries.
- Can add Data-safety by only exposing certain tables and columns in the schema.
- Doesn't expect the LLM to generate executable code, rather behaves as an reasoning engine
- reduced hallucinations and more deterministic in nature
- no need for vector DBs
- Supports all relational databases supported by sql alchemy. Refer https://docs.sqlalchemy.org/en/20/dialects/


# How to Run?
```
docker pull dhanilan/dbchat
docker run -p 5173:5173 -p 8000:8000 dhanilan/dbchat
```
default  database to save connections and conversation is mongo at `mongodb://localhost:27017/dbchat`

if you want to save them at specific mongo database pass it as an env
```
docker run  -p 5173:5173 -p 8000:8000 -e DB_URL=mongodb://localhost:27017/dbchat dhanilan/dbchat

```

if you want to run spider dataset from https://yale-lily.github.io/spider

```
docker run  -p 5173:5173 -p 8000:8000 -e DB_URL=mongodb://localhost:27017/dbchat -e ATTACH_SPIDER_DATASET=1 dhanilan/dbchat

```

## using docker-compose

The docker compose also comes with a chinook database for testing. You can use it by adding a connection to the chinook database in the UI
use  `postgresql+psycopg2://postgres:postgres@chinook:5143/chinook` as the connection string

update the docker-compose.yml with the required envs if neccessary and run
```
docker-compose up -d
```

# Architecture
Built with Autogen.

![alt text](https://github.com/dhanilan/dbchat/blob/main/architecture.png?raw=true)


# Development

Dev container contains all the necessary deps , mongodb storing the schema and chat history , conversations, settings etc
and also a chinook database in postgres for playing around


## Installing dependencies
### UI
`pip install -r requirements.txt`

## server
`cd src/ui && npm i`


## To run the Application in local

### UI
`cd src/ui &&  npm run dev`

### API
`cd src && uvicorn api.main:app`


### Open the UI
By default opens in http://localhost:5173/

Goto setting to save the OPEN AI API key

## connect to dev container chinook db

`postgresql+psycopg2://postgres:postgres@localhost:5432/chinook`



## Roadmap
- [ ] clean up some code for now
- [ ] Add more tests
- [ ] add feature to annotate the schema
- [ ] add few shots of the conversation to the schema
- [ ] add feature to add custom prompts
- [ ] add access control for tables and columns
