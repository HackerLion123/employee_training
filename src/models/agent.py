from langchain_community.chat_models import ChatOllama
from langgraph.graph import END, MessageGraph, StateGraph, START
from langgraph.checkpoint.memory import MemorySaver

from langchain_core.messages import BaseMessage, HumanMessage, SystemMessage
from langgraph.graph.message import add_messages

from IPython.display import Image, display
from langchain_core.pydantic_v1 import BaseModel, Field
from typing import List, TypedDict, Annotated, Sequence
from langchain_core.runnables.graph import MermaidDrawMethod
from langchain_core.output_parsers import JsonOutputParser, StrOutputParser
from typing_extensions import Literal

from langchain.globals import set_llm_cache
from langchain.cache import SQLiteCache


from src.models.rag import create_retriver
from src.helper.utlis import format_docs
from src.models.prompt import (
    create_ragqa_prompt,
    create_rerank_prompt,
    create_router_prompt,
    create_qe_prompt,
    create_hallucination_prompt,
    create_answer_grader_prompt,
)
from src import config

set_llm_cache(SQLiteCache(database_path=config.LLM_CACHE_PATH))


class GraphState(TypedDict):
    """
    Represents the state of our graph.

    Attributes:
        messages: Chat messages
        generation: LLM generation
        documents: list of documents
    """

    question: str
    # messages: Annotated[Sequence[BaseMessage], add_messages]
    generation: str
    documents: List[str]


class Grade(BaseModel):
    """Binary score for relevance check."""

    score: str = Field(description="Relevance score 'yes' or 'no'")


class Feedback(BaseModel):
    grade: Literal["good", "bad"] = Field(
        description="",
    )
    feedback: str = Field(
        description="",
    )


class ChatAgent:

    def __init__(self) -> None:
        self.messages = []
        self.llm = ChatOllama(**config.MODEL_CONFIG)
        self.retriver = create_retriver()
        self.workflow = None
        self.agent = None

    def build(self):
        self._create_workflow()

    def _create_workflow(self):
        self.workflow = StateGraph(GraphState)
        self.workflow.add_node("grade_docs", self._retrivel_grader)
        self.workflow.add_node("retrieve", self._retrive_docs)
        self.workflow.add_node("generate", self._rag_qa)
        self.workflow.add_node("evaluate", self._evaluate_response)
        # self.workflow.add_node("sql_qa", self._sql_agent)
        # self.workflow.add_node("expand_query", self._expand_query)

        self.workflow.add_edge(START, "retrieve")
        # self.workflow.add_edge(START, "expand_query")
        # self.workflow.add_conditional_edges(
        #     START,
        #     self._route_model,
        #     {
        #         "rag": "retrieve",
        #         "db": "sql_qa",
        #     },
        # )
        self.workflow.add_edge("retrieve", "grade_docs")
        self.workflow.add_edge("grade_docs", "generate")
        self.workflow.add_edge("generate", END)
        # self.workflow.add_edge("generate", "evaluate")
        # self.workflow.add_edge("evaluate", END)
        # self.workflow.add_edge("sql_qa", END)
        self.agent = self.workflow.compile()

    def _retrive_docs(self, state):
        question = state["question"]
        documents = self.retriver.get_relevant_documents(question)

        return {"documents": documents, "question": question}

    def _route_model(self, state):
        prompt = create_router_prompt()

        router = prompt | self.llm | JsonOutputParser()

        question = state["question"]
        # router.invoke()

    def _sql_agent(self, state):
        pass

    def _evaluate_response(self, state):
        """_summary_

        Args:
            state (_type_): _description_

        Returns:
            _type_: _description_
        """
        question = state["question"]
        documents = state["documents"]
        generation = state["generation"]

        # prompt = create_hallucination_prompt()

        # hallucination_grader = prompt | self.llm | JsonOutputParser()
        # score = hallucination_grader.invoke(
        #     {"documents": format_docs(documents), "generation": generation}
        # )
        # grade = score["score"]

        prompt = create_answer_grader_prompt()
        answer_grader = prompt | self.llm | JsonOutputParser()

        # Check hallucination
        # if grade == "yes":
        # print("Decided that GENERATION IS GROUNDED IN DOCUMENTS---")
        # Check question-answering
        print("---GRADE GENERATION vs QUESTION---")
        score = answer_grader.invoke({"question": question, "generation": generation})
        grade = score["score"]
        print(grade)
        if grade == "yes":
            return {
                "documents": documents,
                "question": question,
                "generation": generation,
            }
        else:
            return {
                "documents": documents,
                "question": question,
                "generation": """ Sorry I don't have enough context for the question asked. \n 
Cannot provide a reliable answer at the movement please add more context. \n 
I can answers questions about store procedures, policies and other related topics. \n""",
            }
        # else:
        #     print("Answer is not grounded in facts")
        #     return {
        #         "documents": documents,
        #         "question": question,
        #         "generation": generation,
        #     }

    def _expand_query(self, state):
        prompt = create_qe_prompt()

        expand_query = prompt | self.llm | StrOutputParser()

        question = state["question"]
        expanded_question = expand_query.invoke({"question": question})
        print(f"Expanded Query: {expanded_question}")
        return {"question": expanded_question}

    def _retrivel_grader(self, state):
        """_summary_

        Args:
            state (_type_): _description_

        Returns:
            _type_: _description_
        """
        prompt = create_rerank_prompt()
        retrieval_grader = prompt | self.llm | JsonOutputParser()

        print("Check Document Relevance")
        question = state["question"]
        documents = state["documents"]

        # Score each doc
        filtered_docs = []
        for doc in documents:
            score = retrieval_grader.invoke(
                {"question": question, "document": doc.page_content}
            )
            print(score)
            grade = score["score"]
            if grade == "yes":
                filtered_docs.append(doc)
            else:
                continue
        return {"documents": filtered_docs, "question": question}

    def _rag_qa(self, state):
        prompt = create_ragqa_prompt()
        question = state["question"]
        documents = state["documents"]
        rag_chain = prompt | self.llm | StrOutputParser()
        generation = rag_chain.invoke(
            {"context": format_docs(documents), "question": question}
        )

        return {
            "documents": documents,
            "question": question,
            "generation": generation,
        }

    def chat(self, question):
        return self.agent.invoke(question)

    def display_graph(self):
        if self.workflow:
            display(
                Image(
                    self.agent.get_graph().draw_mermaid_png(
                        draw_method=MermaidDrawMethod.API
                    )
                )
            )


if __name__ == "__main__":
    model = ChatAgent()
    model.build()
    # model.display_graph()
    print(model.chat({"question": "how to secure high value items?"}))
