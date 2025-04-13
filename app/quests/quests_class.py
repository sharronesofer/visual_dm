from dataclasses import dataclass
from typing import List

@dataclass
class QuestLogEntry:
    region: str
    poi: str
    timestamp: str
    summary: str
    tags: List[str]
    source: str
    player_id: str

    def to_dict(self):
        return self.__dict__
