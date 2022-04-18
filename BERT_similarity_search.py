import pandas as pd
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np
import json

dataset = pd.read_json('Data/question-answer-dataset.json')


model = SentenceTransformer('bert-base-nli-mean-tokens')
questions = dataset['question']
questions = questions.unique()
question_embeddings = model.encode(questions)

test_sentence = "Irregular periods"
test_embedding = model.encode([test_sentence])

similarity_array = cosine_similarity(
    [test_embedding[0]],
    question_embeddings
)

question_array = questions.copy()

df = pd.DataFrame(np.vstack((question_array, similarity_array)).transpose(), columns=['question', 'score'])
df.sort_values(by=['score'], ascending=False)
print(1)
print(df.head)