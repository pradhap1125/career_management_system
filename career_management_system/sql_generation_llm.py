import os

from langchain_community.llms import Ollama
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.prompts import PromptTemplate
from SQL_Prompt import SQL_PROMPT
import sqlparse
import google.generativeai as genai


os.environ["GOOGLE_API_KEY"] = "<API_KEY>"
genai.configure(api_key=os.environ["GOOGLE_API_KEY"])
# Load LLaMA model and tokenizer
model= ChatGoogleGenerativeAI(
    model="gemini-2.0-flash-thinking-exp-01-21",
    temperature=0,
    max_tokens=None,
    timeout=None,
    max_retries=2,
    # other params...
)

def generate_sql(user_query, history=[]):
    # Initialize the Ollama model
#    llm = Ollama(model="llama3")
    llm = model

    # Format the history into a conversational context
    history_text = "\n".join([f"User: {q}\nAI: {a}" for q, a in history])

    # Define the prompt template
    prompt_template = PromptTemplate(
        input_variables=["query", "history"],
        template=SQL_PROMPT + "\n{history}\nUser Query: {query}\nAI: ",
    )

    # Format the prompt with the user's query and history
    formatted_prompt = prompt_template.format(query=user_query, history=history_text)

    # Get the SQL query from the model
    #response = llm(formatted_prompt)
    response = llm.invoke(formatted_prompt)
    sql_response = response.content.strip()
    # Append current interaction to history
    history.append((user_query, sql_response))

    return sql_response

def is_valid_sql(query: str) -> bool:
    if 'select' in query.lower() and 'from' in query.lower():
       return True
    else:
       return False


if __name__ == "__main__":
    history = []
    user_query = "List applicants who have a certification from Google."
    sql_output = generate_sql(user_query, history)
    print("Generated SQL Query:\n", sql_output)

    if is_valid_sql(sql_output):
        print("Valid SQL Query")