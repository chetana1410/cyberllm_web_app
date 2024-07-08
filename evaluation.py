import pandas as pd
from datasets import Dataset, Features, Value, Sequence, DatasetDict
import google.auth
from langchain_google_vertexai import ChatVertexAI, VertexAIEmbeddings
from ragas import evaluate
from ragas.metrics import (
    faithfulness,
    answer_relevancy,
    answer_similarity,
    answer_correctness,
    context_entity_recall,
)

def evaluate_question_answer(question: str, ground_truth: str, answer: str, contexts: str) -> pd.DataFrame:
    features = Features({
        'question': Value('string'),
        'ground_truth': Value('string'),
        'answer': Value('string'),
        'contexts': Sequence(Value('string'))
    })

    data = {
        'question': [question],
        'ground_truth': [ground_truth],
        'answer': [answer],
        'contexts': [[contexts]]
    }

    dataset = Dataset.from_dict(data, features=features)
    dataset = dataset.map(lambda x: {"contexts": [x['contexts']] if isinstance(x['contexts'], str) else x['contexts']})
    dataset_dict = DatasetDict({'eval': dataset})

    config = {
        "project_id": "aristiun-webapp",
        "chat_model_id": "gemini-1.0-pro-001",
        "embedding_model_id": "textembedding-gecko",
    }

    creds, _ = google.auth.default(quota_project_id=config["project_id"])

    vertextai_llm = ChatVertexAI(
        credentials=creds,
        model_name=config["chat_model_id"],
    )
    vertextai_embeddings = VertexAIEmbeddings(
        credentials=creds, model_name=config["embedding_model_id"]
    )

    metrics = [
        faithfulness,
        answer_relevancy,
        answer_similarity,
        answer_correctness,
        context_entity_recall,
    ]

    result = evaluate(
        dataset_dict['eval'].select(range(1)), 
        metrics=metrics,
        llm=vertextai_llm,
        embeddings=vertextai_embeddings,
    )

    df = result.to_pandas()
    df.drop(columns=['question', 'ground_truth', 'answer', 'contexts'], inplace=True)
    return df
