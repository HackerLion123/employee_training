from ragas import evaluate
from ragas.metrics import (
    answer_relevancy,
    faithfulness,
    context_recall,
    context_precision,
)
from src.models.rag import RAGSearch

import pandas as pd


def rag_evaluation(chat_model, embed_model):
    """_summary_"""
    evaluation_data = pd.DataFrame([])

    result = evaluate(
        evaluation_data["eval"],
        metrics=[
            context_precision,
            faithfulness,
            answer_relevancy,
            context_recall,
        ],
        llm=chat_model,
        embeddings=embed_model,
        raise_exceptions=False,
    )

    results = result.to_pandas()
    return results


def agent_evaluation():
    pass
