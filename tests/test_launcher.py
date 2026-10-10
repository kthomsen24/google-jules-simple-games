import unittest
import tkinter as tk
from main import GameLauncher
from games.snake import SnakeGame
from games.breakout import BreakoutGame


class TestGameLauncher(unittest.TestCase):
    def setUp(self):
        self.app = GameLauncher()
        self.app.withdraw()

    def tearDown(self):
        self.app.destroy()

    def test_launcher_navigation(self):
        self.assertIsNotNone(self.app.current_frame)

        # Launch Snake
        self.app.start_snake()
        self.assertIsInstance(self.app.current_frame, SnakeGame)

        # Return to menu
        self.app.show_menu()
        self.assertNotIsInstance(self.app.current_frame, SnakeGame)

        # Launch Breakout
        self.app.start_breakout()
        self.assertIsInstance(self.app.current_frame, BreakoutGame)


if __name__ == "__main__":
    unittest.main()
