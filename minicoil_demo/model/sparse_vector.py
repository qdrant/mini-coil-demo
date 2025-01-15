from typing import List
import mmh3
from minicoil_demo.model.mini_coil import MiniCOIL
from minicoil_demo.model.stopwords import english_stopwords
from fastembed.common.utils import get_all_punctuation

from qdrant_client import models

GAP = 32000
INT32_MAX = 2**31 - 1

def normalize_vector(vector: List[float]) -> List[float]:
    norm = sum([x ** 2 for x in vector]) ** 0.5
    return [x / norm for x in vector]

def unkn_word_token_id(word: str, shift: int) -> int:  #2-3 words can collied in 1 index with this mapping, not considering mm3 collisions
    hash = mmh3.hash(word)

    if hash < 0:
        unsigned_hash = hash + 2**32
    else:
        unsigned_hash = hash

    range_size = INT32_MAX - shift
    remapped_hash = shift + (unsigned_hash % range_size)
    
    return remapped_hash

def bm25_tf(num_occurrences: int, sentence_len: int, k: float = 1.2, b: float = 0.75, avg_len: float = 256.0) -> float:
    #omitted checking token_max_lenth
    res = num_occurrences * (k + 1)
    res /= num_occurrences + k * (1 - b + b * sentence_len / avg_len)
    return res

def embedding_to_vector(model: MiniCOIL, sentence_embedding: List[dict]) -> models.SparseVector:
    indices = []
    values = []
    
    embedding_size = model.output_dim
    vocab_size = model.vocab_resolver.vocab_size() #mini_coil.vocab_resolver.vocab_size() returns "vocab_size + 1" ("-1" to any word)
    
    #still dependent on vocab_size :(
    unknown_words_shift = ((vocab_size * embedding_size) // GAP + 2) * GAP #miniCOIL vocab + at least (32000 // embedding_size) + 1 new words gap
    
    punctuation = set(get_all_punctuation())
    special_tokens = ['[CLS]', '[SEP]', '[PAD]', '[UNK]', '[MASK]'] #TBD do better

    #we can't use fastembed's def remove_non_alphanumeric(text: str) unless propagating it right to vocab_resolver
    sentence_len = 0
    for embedding in sentence_embedding.values():
        if embedding["word"] not in punctuation and embedding["word"] not in english_stopwords and embedding["word"] not in special_tokens:
            sentence_len += embedding["count"] 
 
    #print(f"Sentence len is {sentence_len}")

    #BM25 will always return a positive value, miniCOIL - nope
    #So, if a word is familiar to miniCOIL, and in one text it's with a +sign (in some dims of the 4 dims), 
    #while in another it has a -sign in the same dim, then we penalize the match between these documents compared to the documents where this word is not present
    #maybe it's not so good(?)

    for embedding in sentence_embedding.values():
        word_id = embedding["word_id"]
        num_occurences = embedding["count"]

        if word_id >= 0: #miniCOIL starts with ID 1
            #print(f"""We counted {num_occurences} occurences of \"{embedding["word"]}\"""")
            embedding = embedding["embedding"]
            normalized_embedding = normalize_vector(embedding)
            for val_id, value in enumerate(normalized_embedding):
                indices.append((word_id - 1) * embedding_size + val_id) #since miniCOIL IDs start with 1
                values.append(value * bm25_tf(num_occurences, sentence_len))
        if word_id == -1: #unk
            if embedding["word"] not in punctuation and embedding["word"] not in english_stopwords and embedding["word"] not in special_tokens:
                #print(f"""We counted {num_occurences} occurences of \"{embedding["word"]}\"""")
                indices.append(unkn_word_token_id(embedding["word"], unknown_words_shift))
                values.append(bm25_tf(num_occurences, sentence_len))
    
    return models.SparseVector(
        indices=indices,
        values=values,
    )