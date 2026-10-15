from __future__ import annotations

from dataclasses import dataclass
from typing import Sequence


@dataclass
class MetricResult:
    name: str
    score: float
    note: str


class HeuristicMetrics:
    """Heuristic metrics for lightweight, non-LLM checks such as overlap and length-based scoring."""

    # candidate = model output, reference is the actual_output or ground truth
    @staticmethod
    def bleu_score(candidate: str, reference: str) -> MetricResult:
        """
        Purpose: Approximate the BLEU metric by measuring word overlap between the answer and the reference.
        What it does: Splits both texts into lowercase words and counts how many candidate words also appear in the reference.
        Returns: A MetricResult whose score is the overlap ratio (matched candidate words divided by total candidate words), higher is better.
        """
        # Split the candidate answer into words.
        # input: candidate = "The cat sat on the mat"
        # output: candidate_words = ['the', 'cat', 'sat', 'on', 'the', 'mat']
        candidate_words = candidate.lower().split()
        # Split the reference answer into words.
        # input: reference = "A cat is sitting on the mat"
        # output: reference_words = ['a', 'cat', 'is', 'sitting', 'on', 'the', 'mat']
        reference_words = reference.lower().split()
        # Count how many candidate words appear in the reference.
        # input: candidate_words = ['the', 'cat', 'sat', 'on', 'the', 'mat'], reference_words = ['a', 'cat', 'is', 'sitting', 'on', 'the', 'mat']
        # output: overlap = 5
        overlap = sum(1 for word in candidate_words if word in reference_words)
        # Compute the overlap ratio.
        # input: overlap = 5, candidate_words length = 6
        # output: score = 0.833
        score = overlap / max(len(candidate_words), 1)
        # Return the result as a MetricResult object.
        # input: score = 0.833
        # output: MetricResult(name="BLEU", score=0.833, note="Higher is better.")
        return MetricResult(name="BLEU", score=round(score, 3), note="Higher is better.")

    @staticmethod
    def rouge_score(candidate: str, reference: str) -> MetricResult:
        """
        Purpose: Approximate the ROUGE metric by measuring how much of the reference is covered by the answer.
        What it does: Turns both texts into sets of unique lowercase words and computes the overlap relative to the reference.
        Returns: A MetricResult whose score is the overlap ratio (shared words divided by reference words), higher is better.
        """
        # Turn the candidate answer into a set of words.
        # input: candidate = "The cat sat on the mat"
        # output: candidate_words = {'the', 'cat', 'sat', 'on', 'mat'}
        candidate_words = set(candidate.lower().split())
        # Turn the reference answer into a set of words.
        # input: reference = "A cat is sitting on the mat"
        # output: reference_words = {'a', 'cat', 'is', 'sitting', 'on', 'the', 'mat'}
        reference_words = set(reference.lower().split())
        # Compute the overlap between the two sets.
        # input: candidate_words = {'the', 'cat', 'sat', 'on', 'mat'}, reference_words = {'a', 'cat', 'is', 'sitting', 'on', 'the', 'mat'}
        # output: score = 0.571 (4 shared words / 7 reference words)
        score = len(candidate_words & reference_words) / max(len(reference_words), 1)
        # Return the result as a MetricResult object.
        # input: score = 0.571
        # output: MetricResult(name="ROUGE", score=0.571, note="Higher is better.")
        return MetricResult(name="ROUGE", score=round(score, 3), note="Higher is better.")

    @staticmethod
    def meteor_score(candidate: str, reference: str) -> MetricResult:
        """
        Purpose: Approximate the METEOR metric with a slightly more flexible word-overlap check.
        What it does: Turns both texts into sets of unique lowercase words and computes the overlap relative to the reference.
        Returns: A MetricResult whose score is the overlap ratio (shared words divided by reference words), higher is better.
        """
        # Turn the candidate answer into a set of words.
        # input: candidate = "The cat sat on the mat"
        # output: candidate_words = {'the', 'cat', 'sat', 'on', 'mat'}
        candidate_words = set(candidate.lower().split())
        # Turn the reference answer into a set of words.
        # input: reference = "A cat is sitting on the mat"
        # output: reference_words = {'a', 'cat', 'is', 'sitting', 'on', 'the', 'mat'}
        reference_words = set(reference.lower().split())
        # Compute the overlap between the two sets.
        # input: candidate_words = {'the', 'cat', 'sat', 'on', 'mat'}, reference_words = {'a', 'cat', 'is', 'sitting', 'on', 'the', 'mat'}
        # output: score = 0.571 (4 shared words / 7 reference words)
        score = len(candidate_words & reference_words) / max(len(reference_words), 1)
        # Return the result as a MetricResult object.
        # input: score = 0.571
        # output: MetricResult(name="METEOR", score=0.571, note="Higher is better.")
        return MetricResult(name="METEOR", score=round(score, 3), note="Higher is better.")

    @staticmethod
    def bertscore_score(candidate: str, reference: str) -> MetricResult:
        """
        Purpose: Approximate semantic similarity (in place of true BERTScore) using shared words as a simple proxy.
        What it does: Turns both texts into sets of unique lowercase words and computes the overlap relative to the reference.
        Returns: A MetricResult whose score is the overlap ratio (shared words divided by reference words), higher is better.
        """
        # Turn the candidate answer into a set of words.
        # input: candidate = "The cat sat on the mat"
        # output: candidate_words = {'the', 'cat', 'sat', 'on', 'mat'}
        candidate_words = set(candidate.lower().split())
        # Turn the reference answer into a set of words.
        # input: reference = "A cat is sitting on the mat"
        # output: reference_words = {'a', 'cat', 'is', 'sitting', 'on', 'the', 'mat'}
        reference_words = set(reference.lower().split())
        # Compute the overlap between the two sets.
        # input: candidate_words = {'the', 'cat', 'sat', 'on', 'mat'}, reference_words = {'a', 'cat', 'is', 'sitting', 'on', 'the', 'mat'}
        # output: score = 0.571 (4 shared words / 7 reference words)
        score = len(candidate_words & reference_words) / max(len(reference_words), 1)
        # Return the result as a MetricResult object.
        # input: score = 0.571
        # output: MetricResult(name="BERTScore", score=0.571, note="Higher is better.")
        return MetricResult(name="BERTScore", score=round(score, 3), note="Higher is better.")

    @staticmethod
    def length_penalty(text: str, min_words: int = 20) -> MetricResult:
        """
        Purpose: Check whether the response is long enough to be considered substantive.
        What it does: Counts the words in the response and compares the count against a minimum-word threshold.
        Returns: A MetricResult whose score is 1.0 if the response meets the minimum word count, otherwise 0.0.
        """
        # Count the words in the response.
        # input: text = "one two three four five"
        # output: word_count = 5
        word_count = len(text.split())
        # Give a full score when the answer is long enough.
        # input: word_count = 5, min_words = 20
        # output: score = 0.0
        score = 1.0 if word_count >= min_words else 0.0
        # Return the result as a MetricResult object.
        # input: score = 0.0
        # output: MetricResult(name="Length Penalty", score=0.0, note="Higher is better.")
        return MetricResult(name="Length Penalty", score=round(score, 3), note="Higher is better.")
