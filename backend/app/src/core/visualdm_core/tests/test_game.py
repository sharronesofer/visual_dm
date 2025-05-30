import unittest
import os
from visualdm_core.game import GameEngine, PlayerState, WorldState, GameState
from visualdm_core.storage import Storage
from visualdm_core.config import Config

class TestGameEngine(unittest.TestCase):
    def setUp(self):
        self.config = Config()
        self.storage = Storage(save_path="test_game_state.json")
        self.engine = GameEngine(config=self.config, storage=self.storage)

    def tearDown(self):
        if os.path.exists("test_game_state.json"):
            os.remove("test_game_state.json")

    def test_initialization(self):
        self.assertIsInstance(self.engine.state.player, PlayerState)
        self.assertIsInstance(self.engine.state.world, WorldState)
        self.assertEqual(self.engine.state.world.turn, 0)

    def test_turn_progression(self):
        self.engine.process_turn()
        self.assertEqual(self.engine.state.world.turn, 1)
        for _ in range(9):
            self.engine.process_turn()
        self.assertEqual(self.engine.state.world.turn, 10)

    def test_save_and_load_state(self):
        self.engine.state.player.name = "Tester"
        self.engine.state.world.turn = 42
        self.storage.save_state(self.engine.state)
        loaded_state = self.storage.load_state()
        self.assertEqual(loaded_state.player.name, "Tester")
        self.assertEqual(loaded_state.world.turn, 42)

if __name__ == "__main__":
    unittest.main() 