import unittest
import tkinter as tk
from main import GameLauncher
from games.snake import SnakeGame
from games.breakout import BreakoutGame
from games.wordle import WordleGame
from games.six_degrees import SixDegreesGame


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

        # Return to menu
        self.app.show_menu()

        # Launch Wordle
        self.app.start_wordle()
        self.assertIsInstance(self.app.current_frame, WordleGame)

        # Return to menu
        self.app.show_menu()

        # Launch Six Degrees of Wikipedia
        self.app.current_frame.destroy()
        self.app.current_frame = SixDegreesGame(self.app, return_to_menu_callback=self.app.show_menu, use_network=False)
        self.assertIsInstance(self.app.current_frame, SixDegreesGame)


if __name__ == "__main__":
    unittest.main()
