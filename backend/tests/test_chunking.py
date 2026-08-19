import unittest

from app.chunking import make_chunks, sentence_windows


RECORD = {
    "query_id": 42,
    "query_type": "DESCRIPTION",
    "query": "गरुड किती वेगाने उडतो?",
    "Answer": "गरुड ताशी १६० किमी वेगाने उडू शकतो.",
    "Eng_Query": "How fast does an eagle fly?",
    "Eng_Answer": "An eagle can fly at 100 mph.",
    "passages": {
        "is_selected": [1, 0],
        "Translated_passages": ["हे पहिले वाक्य आहे. हे दुसरे वाक्य आहे.", "निवडलेले नाही."],
        "English_passages": ["This is sentence one. This is sentence two.", "Not selected."],
    },
}


class ChunkingTests(unittest.TestCase):
    def test_sentence_windows_overlap(self) -> None:
        windows = sentence_windows("One. Two. Three.", size=2, overlap=1)
        self.assertEqual(windows, ["One. Two.", "Two. Three.", "Three."])

    def test_multi_view_chunks_are_stable_and_positive_only(self) -> None:
        first = list(make_chunks(RECORD, "mr"))
        second = list(make_chunks(RECORD, "mr"))
        self.assertEqual(
            {chunk.strategy for chunk in first},
            {"atomic_passage", "sentence_window", "parent_child", "query_answer_anchor"},
        )
        self.assertEqual([chunk.id for chunk in first], [chunk.id for chunk in second])
        self.assertTrue(all(chunk.passage_index == 0 for chunk in first))
        self.assertEqual({chunk.locale for chunk in first}, {"mr", "en"})

    def test_negatives_can_be_included_deliberately(self) -> None:
        chunks = list(make_chunks(RECORD, "mr", include_negatives=True, index_english=False))
        self.assertTrue(any(not chunk.selected for chunk in chunks))
