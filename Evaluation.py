

from sklearn.feature_extraction.text import TfidfVectorizer
import numpy as np
import bert_score
import os
import openai
import json
import pandas as pd
from nltk.tokenize import word_tokenize
from nltk import ngrams
import nltk
import jieba
from Config import *


"""
Several evaluation metrics:

The first one checks for grammatical correctness.

The second one utilizes code embeddings for scoring, which can be done.

The third one uses two methods: Jaccard similarity and BERTScore.
"""

# Replace with your OpenAI API key
openai.api_key = OPENAI_API_KEY
nltk.download('punkt')

def jaccard_similarity(set1, set2):
    set1 = set(set1)
    set2 = set(set2)
    intersection = set1.intersection(set2)
    union = set1.union(set2)
    return len(intersection) / len(union)

def compute_tfidf_vectors(sentences):
    vectorizer = TfidfVectorizer()
    tfidf_matrix = vectorizer.fit_transform(sentences)
    tfidf_vectors = tfidf_matrix.toarray()
    return tfidf_vectors

def compute_bm25_similarity(tfidf_vectors, k1=1.5, b=0.75):
    doc1_tf = tfidf_vectors[0]
    doc2_tf = tfidf_vectors[1]
    doc_len = np.sum(doc1_tf)  # Total term count in the document
    doc_len_avg = np.mean(np.sum(tfidf_vectors, axis=1))  # Average document length

    idf = np.log((len(tfidf_vectors) + 1) / (np.count_nonzero(tfidf_vectors, axis=0) + 1)) + 1
    idf[idf < 0] = 0  # Replace negative idf values with 0

    bm25_sim = np.sum((doc1_tf * (k1 + 1)) / (doc1_tf + k1 * (1 - b + b * doc_len / doc_len_avg)) * doc2_tf * idf)

    return bm25_sim

def bm25_similarity(sentence1, sentence2):
    # Tokenize the sentences
    tokens1 = jieba.lcut(sentence1.lower())
    tokens2 = jieba.lcut(sentence2.lower())

    # Compute Jaccard similarity between the sentences
    jaccard_sim = jaccard_similarity(tokens1, tokens2)

    # Combine the sentences for vectorization
    combined_sentences = [sentence1, sentence2]

    # Compute TF-IDF vectors
    tfidf_vectors = compute_tfidf_vectors(combined_sentences)

    # Compute BM25 similarity
    bm25_sim = compute_bm25_similarity(tfidf_vectors)

    # Normalize the similarities
    jaccard_sim = jaccard_sim / 1.0  # Jaccard similarity is already in [0, 1]
    bm25_sim = (bm25_sim + 1) / 2.0  # Normalize BM25 similarity to [0, 1]

    # Combine TF-IDF, BM25, and Jaccard using weighted sum
    combined_sim = (0.5 * jaccard_sim) + (0.3 * bm25_sim) + (0.2 * tfidf_vectors[0].dot(tfidf_vectors[1]))
    return combined_sim

def calculate_bert_score(sentence1, sentence2, model_type='bert-base-multilingual-cased'):
    # Calculate BERTScore using bert-score
    P, R, F1 = bert_score.score([sentence1], [sentence2], model_type=model_type)
    bert_score_value = F1.item()
    return bert_score_value

def calculate_cosine_similarity(vector1, vector2):
    # Calculate cosine similarity between two vectors
    dot_product = sum(a * b for a, b in zip(vector1, vector2))
    magnitude1 = sum(a ** 2 for a in vector1) ** 0.5
    magnitude2 = sum(b ** 2 for b in vector2) ** 0.5
    cosine_similarity = dot_product / (magnitude1 * magnitude2)
    return cosine_similarity

def calculate_code_similarity(sentence1, sentence2):
    # Set OpenAI API key

    # Call openai.Embed API to get embeddings for sentences

    response = openai.Embedding.create(model="text-embedding-ada-002", input=[sentence1, sentence2])
    embedding1 = response['data'][0]['embedding']
    embedding2 = response['data'][1]['embedding']

    # Calculate sentence similarity, e.g., using cosine similarity
    similarity = calculate_cosine_similarity(embedding1, embedding2)

    return similarity

def evaluation(gpt_result, gold_result, gpt_gql, gold_gql):
    # Syntax score
    syntax_score = 0
    if gpt_result == [] or gpt_result == '[]':
        syntax_score = 1
    elif gpt_result[0] == '语法错误':
        syntax_score = 0
    else:
        syntax_score = 1

    # Code similarity
    code_score = calculate_code_similarity(gpt_gql, gold_gql)

    # Lexical similarity
    gql_result = str(gpt_result) if str(gpt_result) != '[]' else 'null_aaaaaaaa'
    result = str(gold_result) if str(gold_result) != '[]' else 'null_aaaaaaaa'

    if len(gql_result) > 9 and len(result) > 9:
        if syntax_score == 1:
            if str(gql_result) == str(result):
                bm25_score_temp = 1
            elif len(str(gql_result)) == len(str(result)):
                bm25_score_temp = 0
            else:
                bm25_score_temp = bm25_similarity(gql_result, result)
        else:
            bm25_score_temp = 0
        if syntax_score == 1:
            bert_score_temp = calculate_bert_score(gql_result, result)
        else:
            bert_score_temp = 0
    else:
        if gql_result == result:
            bm25_score_temp = 1
            bert_score_temp = 1
        else:
            bm25_score_temp = 0
            bert_score_temp = 0

    avg_score = (bm25_score_temp + bert_score_temp) / 2
    return syntax_score, code_score, avg_score