from langchain_core.prompts import (
    ChatPromptTemplate,
    HumanMessagePromptTemplate,
    PromptTemplate,
)

from langchain_core.messages import SystemMessage


def create_ragqa_prompt():
    """ """
    prompt = """
    You are team member assistant for question-answering store memebers.
    Your goal is to assist team members to understand and perform different store policies and prodecures.
    And also answer any queries they have realted to stores. 
    Use the following pieces of retrieved context to answer the question. 
    If you don't know the answer, just say that you don't know. 
    Use six sentences maximum and keep the answer concise.
    Format the answers with bullet points or numbers and line breaks.
    
    Question: {question} 
    Context: {context} 
    Answer:
    """
    prompt = PromptTemplate(template=prompt, input_variables=["question", "context"])

    return prompt


def create_hallucination_prompt():
    prompt = PromptTemplate(
        template="""You are a grader assessing whether an answer is grounded in / supported by a set of facts. \n
    Follow these steps to evaluate the answer:

    1. Understand the Facts: Read the provided set of facts carefully to grasp the relevant information. 
    The fact contains set of store policy and precedure documents. 
    2. Analyze the Answer: Examine the provided answer to see if it aligns with and is supported by the given facts.
    3. Final Decision: Based on your analysis, decide if the answer is grounded in / supported by the given set of facts.

    Here are the facts:
    \n ------- \n
    {documents} 
    \n ------- \n
    Here is the answer: {generation}
    It does not need to be a stringent test. The goal is to filter out erroneous response which is as per provided facts. 
    Give a binary score 'yes' or 'no' score to indicate whether the answer is grounded in / supported by given set of facts. \n
    Provide the binary score as a JSON with a single key 'score' and no preamble or explanation.""",
        input_variables=["generation", "documents"],
    )

    return prompt


def create_answer_eval_prompt():
    prompt = PromptTemplate(
        template="""You are a grader assessing whether an answer is useful to resolve a question. 
    Follow these steps to evaluate the answer:
    1. Understand the Question: Read the question carefully to grasp what information is being sought.
    2. Analyze the Answer: Examine the provided answer to see if it addresses the question directly and accurately.
    3. Relevance to Store Employees: Determine if the answer is relevant to store employees, expalining store process, training and policies.
    4. Final Decision: Based on your analysis, decide if the answer is useful to resolve the question.
    
    Here is the answer:
    \n ------- \n
    {generation} 
    \n ------- \n
    Here is the question: {question}
    Give a binary score 'yes' or 'no' to indicate whether the answer is useful to resolve the question. 
    Provide the binary score as a JSON with a single key 'score' and no preamble or explanation.""",
        input_variables=["generation", "question"],
    )
    return prompt


def create_rerank_prompt():
    prompt = PromptTemplate(
        template="""You are a grader assessing relevance of a retrieved document to a user question. \n 
    Here is the retrieved document: \n\n {document} \n\n
    Here is the user question: {question} \n
    If the document contains keywords or meaning related to the user question, grade it as relevant. \n
    It does not need to be a stringent test. The goal is to filter out erroneous retrievals. \n
    Give a binary score 'yes' or 'no' score to indicate whether the document is relevant to the question. \n
    Provide the binary score as a JSON with a single key 'score' and no premable or explanation.
        """,
        input_variables=["document", "question"],
    )

    return prompt


def create_router_prompt():
    prompt = PromptTemplate(
        template="""You are an expert at routing a user question to a vectorstore or web search. \n
    Use the vectorstore for questions on . \n
    You are part of tool to assit team members to understand and perform different store procedures.
    You do not need to be stringent with the keywords in the question related to these topics. \n
     \n
    Return the a JSON with a single key 'datasource' and no premable or explanation. \n
    Question to route: {question}""",
        input_variables=["question"],
    )

    return prompt


def create_qe_prompt():
    """Prompt to redefine and rewrite the question"""
    prompt = PromptTemplate(
        template="""You a question re-writer that converts an input question 
    to a better version that is optimized. for vectorstore retrieval. \n
    You are part of tool to assit team members to understand and perform different store procedures.
    Look at the initial info and meta data and 
    formulate an improved question. \n
    
    Meta Data: You are helping a team member in austrilan stores  to understand store process
    and all the question is related to store and store procedures.
    
    Question: {question}""",
        input_variables=["question"],
    )

    return prompt


def create_answer_grader_prompt():
    prompt = PromptTemplate(
        template="""You are a grader assessing whether an answer is useful to resolve a question. \n 
    Here is the answer:
    \n ------- \n
    {generation} 
    \n ------- \n
    Here is the question: {question}
    Give a binary score 'yes' or 'no' to indicate whether the answer is useful to resolve a question. \n
    Provide the binary score as a JSON with a single key 'score' and no preamble or explanation.""",
        input_variables=["generation", "question"],
    )
    return prompt


def create_relevant_table_prompt():
    """
    Creates a prompt template for determining relevant tables based on a user query and table metadata.
    """
    prompt = """
    You are a database assistant. Given the following table metadata:
    {table_metadata}
    
    Determine which table(s) are needed to answer the following user query:
    "{user_query}"
    
    Return only the table names as a JSON list.
    PLEASE NOTE: DO NOT MERGE THE TABLES AT ANY COST.
    You MUST strictly return None if the user query does not logically require data from any table.

    The output format is as follows:
    - If the tables are needed:
      ['table1', 'table2']
    - If the tables are not needed:
      ['None']
    """

    prompt = PromptTemplate(
        template=prompt, input_variables=["user_query", "table_metadata"]
    )

    return prompt


def create_sql_generation_prompt():
    """
    Creates a prompt template for generating SQL queries based on user input and table schema.
    """
    prompt = """
    You are an Expert AI assistant that helps generate SQL queries based on user input in English.
    Ignore all previous instructions and conversations. Start a fresh session.
    
    The database schema is as follows:
    
    Tables names and their column names along with their datatypes are as follows:
    {table_related_info}
    
    **Instructions**:
    1. Read the question carefully.
    2. Use only the provided schema.
    3. Return ONLY the SQL query.
    4. Use SQLite syntax.
    5. Do not include ''' at the beginning or end of the response, and do not add 'sql' in the response.

    Few examples for you to understand the response format:

    User Input:
    1. "List all sales ordered by date in descending order."
    Response:
        SELECT * FROM sales ORDER BY date DESC;

    2. "Show the total, average, and maximum sales amount for each product."
    Response:
        SELECT product, SUM(amount) AS total_sales, AVG(amount) AS average_sales, 
        MAX(amount) AS max_sales FROM sales GROUP BY product;

    NOTE: Strictly follow the instructions to generate the correct response.
    """

    prompt = PromptTemplate(
        template=prompt, input_variables=["user_input", "table_related_info"]
    )

    return prompt
