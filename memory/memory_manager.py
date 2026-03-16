from memory.short_term_memory import ShortTermMemory
from memory.long_term_memory import LongTermMemory
from memory.episodic_memory import EpisodicMemory
from memory.semantic_memory import SemanticMemory


class MemoryManager:
    def __init__(self):
        self.short_term = ShortTermMemory()
        self.long_term = LongTermMemory()
        self.episodic = EpisodicMemory()
        self.semantic = SemanticMemory()