from src.db_chat.ask import ask_ai

connection_string = "postgresql://dbchatuser:dbchatuser@localhost:5432/dbchatdb"
question = "Find the user who got the most likes"
ask_ai(connection_string, question)
