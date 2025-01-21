from typing import List
import mmh3
from minicoil_demo.model.mini_coil import MiniCOIL
from minicoil_demo.model.stopwords import english_stopwords
from fastembed.common.utils import get_all_punctuation #, remove_non_alphanumeric

from qdrant_client import models

GAP = 32000
INT32_MAX = 2**31 - 1
english_stopwords = set(english_stopwords)
punctuation = set(get_all_punctuation())
special_tokens = set(['[CLS]', '[SEP]', '[PAD]', '[UNK]', '[MASK]'])

def normalize_vector(vector: List[float]) -> List[float]:
    norm = sum([x ** 2 for x in vector]) ** 0.5
    return [x / norm for x in vector]

def unkn_word_token_id(word: str, shift: int) -> int:  #2-3 words can collide in 1 index with this mapping, not considering mm3 collisions
    hash = mmh3.hash(word)

    if hash < 0:
        unsigned_hash = hash + 2**32
    else:
        unsigned_hash = hash

    range_size = INT32_MAX - shift
    remapped_hash = shift + (unsigned_hash % range_size)
    
    return remapped_hash

def bm25_tf(num_occurrences: int, sentence_len: int, avg_len: float = 150.0, k: float = 1.2, b: float = 0.75) -> float:
    res = num_occurrences * (k + 1)
    res /= num_occurrences + k * (1 - b + b * sentence_len / avg_len)
    return res

def embedding_to_vector(model: MiniCOIL, sentence_embedding: dict, avg_len: float = 150.0, token_max_length: int = 40) -> models.SparseVector:
    indices = []
    values = []
    
    embedding_size = model.output_dim
    vocab_size = model.vocab_resolver.vocab_size() #mini_coil.vocab_resolver.vocab_size() returns "vocab_size + 1" ("-1" to any word)
    
    #still dependent on vocab_size :(
    unknown_words_shift = ((vocab_size * embedding_size) // GAP + 2) * GAP #miniCOIL vocab + at least (GAP // embedding_size) + 1 new words gap

    sentence_len = 0
    for embedding in sentence_embedding.values():
        if embedding["word"] not in punctuation | english_stopwords | special_tokens:
            #word = remove_non_alphanumeric(embedding["word"]).strip()
            #imo not so much sense in this while we remove all the money & math symbols, and they actually can help with matching in some queries
            #like then why do we keep numbers

            if len(embedding["word"]) <= token_max_length:
                sentence_len += embedding["count"]


    #BM25 will always return a positive value, miniCOIL - nope
    #So, if a word is familiar to miniCOIL, and in one text it's with a +sign (in some dims of the 4 dims), 
    #while in another it has a -sign in the same dim, then we penalize the match between these documents compared to the documents where this word is not present

    for embedding in sentence_embedding.values():
        word_id = embedding["word_id"]
        num_occurences = embedding["count"]

        if word_id >= 0: #miniCOIL starts with ID 1
            embedding = embedding["embedding"]
            normalized_embedding = normalize_vector(embedding)
            for val_id, value in enumerate(normalized_embedding):
                indices.append((word_id - 1) * embedding_size + val_id) #since miniCOIL IDs start with 1
                values.append(value * bm25_tf(num_occurences, sentence_len, avg_len))
        if word_id == -1: #unk
            if embedding["word"] not in punctuation | english_stopwords | special_tokens:
                #word = remove_non_alphanumeric(embedding["word"]).strip()
                if len(embedding["word"]) <= token_max_length:
                    indices.append(unkn_word_token_id(embedding["word"], unknown_words_shift))
                    values.append(bm25_tf(num_occurences, sentence_len, avg_len))
    return models.SparseVector(
        indices=indices,
        values=values,
    )

def query_embedding_to_vector(model: MiniCOIL, sentence_embedding: dict, token_max_length: int = 40) -> models.SparseVector:
    indices = []
    values = []
    
    embedding_size = model.output_dim
    vocab_size = model.vocab_resolver.vocab_size() #mini_coil.vocab_resolver.vocab_size() returns "vocab_size + 1" ("-1" to any word)
    
    #still dependent on vocab_size :(
    unknown_words_shift = ((vocab_size * embedding_size) // GAP + 2) * GAP #miniCOIL vocab + at least (GAP // embedding_size) + 1 new words gap

    for embedding in sentence_embedding.values():
        word_id = embedding["word_id"]

        if word_id >= 0: #miniCOIL starts with ID 1
            embedding = embedding["embedding"]
            normalized_embedding = normalize_vector(embedding)
            for val_id, value in enumerate(normalized_embedding):
                indices.append((word_id - 1) * embedding_size + val_id) #since miniCOIL IDs start with 1
                values.append(value)
        if word_id == -1: #unk
            if embedding["word"] not in punctuation | english_stopwords | special_tokens:
                #word = remove_non_alphanumeric(embedding["word"]).strip()
                if len(embedding["word"]) <= token_max_length:
                    indices.append(unkn_word_token_id(embedding["word"], unknown_words_shift))
                    values.append(1)
    
    return models.SparseVector(
        indices=indices,
        values=values,
    )