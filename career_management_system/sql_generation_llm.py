from langchain_community.llms import Ollama
from langchain.prompts import PromptTemplate
from SQL_Prompt import SQL_PROMPT
import sqlparse


def generate_sql(user_query, history=[]):
    # Initialize the Ollama model
    llm = Ollama(model="llama3")

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
    response = llm(formatted_prompt)

    # Append current interaction to history
    history.append((user_query, response))
    return response

def is_valid_sql(query: str) -> bool:
    try:
        parsed = sqlparse.parse(query)
        return bool(parsed)
    except Exception:
        return False


if __name__ == "__main__":
    history = []
    user_query = "List applicants who have a certification from Google."
    sql_output, history = generate_sql(user_query, history)
    print("Generated SQL Query:\n", sql_output)

    # Follow-up query example
    follow_up_query = "Show their phone numbers too."
    sql_output, history = generate_sql(follow_up_query, history)
    print("Generated SQL Query:\n", sql_output)