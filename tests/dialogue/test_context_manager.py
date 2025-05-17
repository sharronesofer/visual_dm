import pytest
from datetime import datetime, timedelta
from dialogue.context_manager import ConversationHistory
from dialogue.scoring import relevance_score
from dialogue.extractors import extract_key_info

class DummyEntry:
    def __init__(self, speaker, message, timestamp):
        self.speaker = speaker
        self.message = message
        self.timestamp = timestamp


def test_add_and_retrieve_entries():
    history = ConversationHistory(max_messages=3)
    history.add_entry('user', 'Hello')
    history.add_entry('npc', 'Greetings')
    history.add_entry('user', 'Tell me about the quest')
    history.add_entry('npc', 'The quest is dangerous')
    assert len(history.entries) == 3
    assert history.entries[0].message == 'Greetings'
    assert history.entries[-1].message == 'The quest is dangerous'

def test_context_window_default():
    history = ConversationHistory(max_messages=2)
    history.add_entry('user', 'A')
    history.add_entry('npc', 'B')
    history.add_entry('user', 'C')
    window = history.get_context_window()
    assert len(window) == 2
    assert window[0].message == 'B'
    assert window[1].message == 'C'

def test_context_window_with_scoring():
    now = datetime.utcnow()
    entries = [
        DummyEntry('user', 'quest: Find the sword', now - timedelta(hours=2)),
        DummyEntry('npc_important', 'reward: 100 gold', now - timedelta(hours=1)),
        DummyEntry('npc', 'Be careful!', now - timedelta(minutes=10)),
    ]
    # Score: reward message should be highest due to speaker and keyword
    scored = sorted(entries, key=lambda e: relevance_score(e, now=now), reverse=True)
    assert scored[0].speaker == 'npc_important'
    assert 'reward' in scored[0].message

def test_extract_key_info():
    message = 'The quest: Dragon Hunt offers a reward: 500 gold. Will you accept?'
    info = extract_key_info(message)
    types = {item['type'] for item in info}
    assert 'quest' in types
    assert 'reward' in types

def test_serialization_and_persistence(tmp_path):
    history = ConversationHistory()
    history.add_entry('user', 'Test message')
    file_path = tmp_path / 'history.json'
    history.save(str(file_path))
    loaded = ConversationHistory.load(str(file_path))
    assert loaded.entries[0].message == 'Test message' 