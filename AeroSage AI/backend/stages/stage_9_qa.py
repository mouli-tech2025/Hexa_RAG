# Deliberately implemented manually with AutoModelForQuestionAnswering +
# AutoTokenizer rather than a framework wrapper (e.g. Haystack's
# ExtractiveReader). Same underlying model (deepset/roberta-base-squad2),
# but this gives direct control over span extraction and confidence
# scoring, fewer dependencies, and easier debugging for a hackathon
# timeline.

from typing import List

import torch
from transformers import AutoModelForQuestionAnswering, AutoTokenizer

from config import QA_MODEL


class ExtractiveQA:
    # NOTE: transformers>=5 removed the "question-answering" pipeline task
    # and the QuestionAnsweringPipeline class entirely (confirmed via
    # KeyError against the installed transformers==5.14.1, not guessed).
    # Per user decision, this replicates the same extractive span-scoring
    # logic that pipeline used internally, via AutoModelForQuestionAnswering
    # + AutoTokenizer directly, instead of downgrading transformers.
    def __init__(self) -> None:
        self.is_loaded = False
        self.tokenizer = AutoTokenizer.from_pretrained(QA_MODEL)
        self.model = AutoModelForQuestionAnswering.from_pretrained(QA_MODEL)
        self.model.eval()
        self.is_loaded = True

    def _answer_one(self, question: str, context: str) -> dict:
        inputs = self.tokenizer(
            question,
            context,
            return_tensors="pt",
            truncation=True,
            max_length=384,
            return_offsets_mapping=True,
        )
        offset_mapping = inputs.pop("offset_mapping")[0]
        sequence_ids = inputs.sequence_ids(0)

        with torch.no_grad():
            outputs = self.model(**inputs)

        start_logits = outputs.start_logits[0]
        end_logits = outputs.end_logits[0]

        # Mask out any token that isn't part of the context (question, CLS/SEP).
        context_mask = torch.tensor([sid == 1 for sid in sequence_ids])
        start_logits = start_logits.masked_fill(~context_mask, float("-inf"))
        end_logits = end_logits.masked_fill(~context_mask, float("-inf"))

        start_probs = torch.softmax(start_logits, dim=-1)
        end_probs = torch.softmax(end_logits, dim=-1)

        max_answer_len = 64
        best_score = -1.0
        best_start, best_end = 0, 0
        context_indices = [i for i, sid in enumerate(sequence_ids) if sid == 1]
        for start_idx in context_indices:
            for end_idx in context_indices:
                if end_idx < start_idx or end_idx - start_idx + 1 > max_answer_len:
                    continue
                score = (start_probs[start_idx] * end_probs[end_idx]).item()
                if score > best_score:
                    best_score = score
                    best_start, best_end = start_idx, end_idx

        char_start = offset_mapping[best_start][0].item()
        char_end = offset_mapping[best_end][1].item()
        answer = context[char_start:char_end]

        return {"answer": answer, "score": best_score}

    def answer(self, question: str, chunks: List[dict]) -> List[dict]:
        for chunk in chunks:
            content = chunk.get("content", "")
            if not content:
                chunk["extracted_span"] = ""
                chunk["qa_confidence"] = 0.0
                continue

            try:
                result = self._answer_one(question, content)
                chunk["extracted_span"] = result["answer"]
                chunk["qa_confidence"] = result["score"]
            except Exception:
                chunk["extracted_span"] = ""
                chunk["qa_confidence"] = 0.0

        return chunks


qa_engine = ExtractiveQA()
