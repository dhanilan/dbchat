# Chat with existing Database
LLM powered

Dev container contains all the necessary deps , mongodb storing the schema and chat history , conversations, settings etc
and also a chinook database in postgres for playing around

## install deps

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
- [ ] Complete image as docker and run ui and backend
- [ ] fix bug of connections
- [ ] Test for mysql , pg and sqllite etc
- [ ] put a nice readme with how it works
- [ ] clean up some code for now
