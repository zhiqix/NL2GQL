import os
from enum import Enum
import numpy as np
from Config import *
from Embedding import Embedding
"""
Two levels of retrieval:
One way is to calculate the score by editing the distance
Another way is to calculate scores based on the similarity of embedding vectors
"""
def dependable_faiss_import(no_avx2=None):
    """
    Import Faiss if available, otherwise raise an error.
    If the FAISS_NO_AVX2 environment variable is set, it will be considered
    to load Faiss with no AVX2 optimization.

    Args:
        no_avx2: Load Faiss strictly with no AVX2 optimization
            so that the vector store is portable and compatible with other devices.
    """
    if no_avx2 is None and "FAISS_NO_AVX2" in os.environ:
        no_avx2 = bool(os.getenv("FAISS_NO_AVX2"))

    try:
        if no_avx2:
            from faiss import swigfaiss as faiss
        else:
            import faiss
    except ImportError:
        raise ImportError(
            "Could not import the Faiss Python package. "
            "Please install it with `pip install faiss-gpu` (for CUDA supported GPU) "
            "or `pip install faiss-cpu` (depending on Python version)."
        )
    return faiss

class DistanceStrategy(str, Enum):
    """Enumerator of the Distance strategies for calculating distances
    between vectors."""
    EUCLIDEAN_DISTANCE = "EUCLIDEAN_DISTANCE"
    MAX_INNER_PRODUCT = "MAX_INNER_PRODUCT"
    DOT_PRODUCT = "DOT_PRODUCT"
    JACCARD = "JACCARD"
    COSINE = "COSINE"


def edit_distance(str1, str2):
    """Calculation of Editing Distance"""
    m, n = len(str1), len(str2)

    # Create an (m+1) x (n+1) matrix, initialized to 0
    dp = [[0] * (n + 1) for _ in range(m + 1)]

    # Initialize the first row and column
    for i in range(m + 1):
        dp[i][0] = i
    for j in range(n + 1):
        dp[0][j] = j

    # Fill the matrix
    for i in range(1, m + 1):
        for j in range(1, n + 1):
            if str1[i - 1] == str2[j - 1]:
                cost = 0
            else:
                cost = 1
            dp[i][j] = min(
                dp[i - 1][j] + 1,  # Insert
                dp[i][j - 1] + 1,  # Delete
                dp[i - 1][j - 1] + cost  # Replace
            )

    return dp[m][n]



class FAISS:
    def __init__(self, embeddings, doc_store):
        self.faiss = dependable_faiss_import()
        self.distance_strategy = DISTANCE_STRATEGY
        self.embeddings = embeddings
        self.index = None
        self.normalize_L2 = NORMALIZE_L2
        self.top_k = TOP_K
        doc_store.drop(['embedding'], axis=1, inplace=True)
        self.doc_store = doc_store.to_dict(orient='records')
        if self.distance_strategy == DistanceStrategy.MAX_INNER_PRODUCT:
            self.index = self.faiss.IndexFlatIP(len(embeddings[0]))
        else:
            # Default to L2, currently other metric types are not initialized.
            self.index = self.faiss.IndexFlatL2(len(embeddings[0]))


    def add_all(self):
        """add all embeddings"""
        vector = np.array(self.embeddings, dtype=np.float32)
        if self.normalize_L2:
            self.faiss.normalize_L2(vector)
        self.index.add(vector)

    def search(self, query):
        """search the top_k similarity by vector"""
        top_k = self.top_k
        query_emb = Embedding().embedding_query(query)
        query_emb = np.array(query_emb, dtype=np.float32)
        distance, idx = self.index.search(query_emb.reshape(1, -1), k=top_k)
        return [self.doc_store[i] for i in idx[0]]

    def search_with_char(self, query):
        """calculate the score by editing the distance"""
        top_1 = 0
        max_score = 0
        for dict_i in self.doc_store:
            score = min(len(query), len(str(dict_i)))/edit_distance(query, str(dict_i))
            if score > max_score:
                max_score = score
                top_1 = dict_i
        return top_1
