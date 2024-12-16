"""
End-to-end inference of the miniCOIL model.
This includes sentence transformer, vocabulary resolver, and the coil post-encoder.
"""
import json
from typing import List

import numpy as np
from fastembed.late_interaction.token_embeddings import TokenEmbeddingsModel

from minicoil_demo.model.encoder import Encoder
from minicoil_demo.model.vocab_resolver import VocabResolver, VocabTokenizerTokenizer


class MiniCOIL:

    def __init__(
            self,
            vocab_path: str,
            word_encoder_path: str,
            input_dim: int = 512,
            output_dim: int = 4,
            sentence_encoder_model: str = "jinaai/jina-embeddings-v2-small-en-tokens"
    ):
        self.sentence_encoder_model = sentence_encoder_model
        self.sentence_encoder = TokenEmbeddingsModel(model_name=sentence_encoder_model, threads=1)

        self.vocab_path = vocab_path
        self.vocab_resolver = VocabResolver(tokenizer=VocabTokenizerTokenizer(self.sentence_encoder.tokenizer))
        self.vocab_resolver.load_json_vocab(vocab_path)

        self.input_dim = input_dim
        self.output_dim = output_dim

        self.word_encoder_path = word_encoder_path

        self.word_encoder = None

        self.load_encoder_numpy()

    def load_encoder_numpy(self):
        weights = np.load(self.word_encoder_path)
        self.word_encoder = Encoder(weights)
        assert self.word_encoder.input_dim == self.input_dim
        assert self.word_encoder.output_dim == self.output_dim

    def encode(self, sentences: list) -> List[dict]:
        """
        Encode the given word in the context of the sentences.
        """

        result = []

        for embedding, sentence in zip(self.sentence_encoder.embed(sentences, batch_size=4), sentences):
            token_ids = np.array(self.sentence_encoder.tokenize([sentence])[0].ids)

            word_ids, counts, oov, forms = self.vocab_resolver.resolve_tokens(token_ids)

            print(forms)

            # Size: (1, words)
            word_ids = np.expand_dims(word_ids, axis=0)
            # Size: (1, words, embedding_size)
            embedding = np.expand_dims(embedding, axis=0)

            # Size of word_ids_mapping: (unique_words, 2) - [vocab_id, batch_id]
            # Size of embeddings: (unique_words, embedding_size)
            ids_mapping, embeddings = self.word_encoder.forward(word_ids, embedding)

            # Size of counts: (unique_words)
            words_ids = ids_mapping[:, 0]

            sentence_result = {}

            words = [self.vocab_resolver.lookup_word(word_id) for word_id in words_ids]

            for word, word_id, emb in zip(words, words_ids, embeddings):
                if word_id == 0:
                    continue

                sentence_result[word] = {
                    "word": word,
                    "forms": forms[word],
                    "count": int(counts[word_id]),
                    "word_id": int(word_id),
                    "embedding": emb.tolist()
                }

            for oov_word, count in oov.items():
                sentence_result[oov_word] = {
                    "word": oov_word,
                    "forms": [oov_word],
                    "count": int(count),
                    "word_id": -1,
                    "embedding": [1]
                }

            result.append(sentence_result)

        return result


def main():
    import argparse
    import ipdb

    parser = argparse.ArgumentParser()
    parser.add_argument("--vocab-path", type=str)
    parser.add_argument("--word-encoder-path", type=str)
    parser.add_argument("--sentences", type=str, nargs='+')
    args = parser.parse_args()

    # Catch exception with ipdb

    with ipdb.launch_ipdb_on_exception():
        model = MiniCOIL(
            vocab_path=args.vocab_path,
            word_encoder_path=args.word_encoder_path
        )

        for embeddings in model.encode(args.sentences):
            for word, embedding in embeddings.items():
                print(word, json.dumps(embedding))


if __name__ == '__main__':
    main()
