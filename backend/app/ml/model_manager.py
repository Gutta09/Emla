import os
from app.config import settings
from app.ml.fingerspell_model import FingerspellModel
from app.ml.word_model import WordModel


class ModelManager:
    """Singleton that owns both models and exposes them after startup loading."""

    def __init__(self):
        self.fingerspell: FingerspellModel | None = None
        self.word: WordModel | None = None

    def load_all(self):
        models_dir = settings.models_dir
        fingerspell_dir = os.path.join(models_dir, "fingerspell")
        word_dir = os.path.join(models_dir, "word_signs")

        print("[ModelManager] Loading models...")
        self.fingerspell = FingerspellModel(
            fingerspell_dir, confidence_threshold=settings.confidence_threshold
        )
        self.word = WordModel(
            word_dir, confidence_threshold=settings.confidence_threshold
        )
        print("[ModelManager] All models ready.")

    @property
    def loaded_names(self) -> list[str]:
        names = []
        if self.fingerspell and self.fingerspell.is_loaded:
            names.append("fingerspell")
        if self.word and self.word.is_loaded:
            names.append("word")
        return names

    @property
    def vocabulary_size(self) -> int:
        total = 0
        if self.fingerspell and self.fingerspell.is_loaded:
            total += self.fingerspell.num_classes
        if self.word and self.word.is_loaded:
            total += self.word.num_classes
        return total
