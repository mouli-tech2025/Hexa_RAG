from typing import List

from sentence_transformers import SentenceTransformer

from config import TEXT_EMBED_MODEL


class TextEmbedder:
    def __init__(self) -> None:
        self.is_loaded = False
        self.model = SentenceTransformer(TEXT_EMBED_MODEL)
        self.is_loaded = True

    def embed(self, text: str) -> List[float]:
        return self.model.encode(text).tolist()


text_embedder = TextEmbedder()
