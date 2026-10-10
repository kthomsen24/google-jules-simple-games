import unittest
import tkinter as tk
from games.wordle import WordleGame, COLOR_CORRECT, COLOR_PRESENT, COLOR_ABSENT, DEFAULT_WORD_LENGTH, DEFAULT_MAX_ATTEMPTS


class TestWordleGame(unittest.TestCase):
    def setUp(self):
        self.root = tk.Tk()
        self.root.withdraw()
        self.game = WordleGame(self.root)

    def tearDown(self):
        self.game.unbind_events()
        self.game.destroy()
        self.root.destroy()

    def test_default_initialization(self):
        self.assertEqual(self.game.word_length, DEFAULT_WORD_LENGTH)
        self.assertEqual(self.game.max_attempts, DEFAULT_MAX_ATTEMPTS)
        self.assertEqual(len(self.game.secret_word), 5)
        self.assertFalse(self.game.game_over)
        self.assertFalse(self.game.game_won)
        self.assertEqual(len(self.game.attempts), 0)

    def test_custom_initialization(self):
        custom_game = WordleGame(self.root, word_length=6, max_attempts=4)
        self.assertEqual(custom_game.word_length, 6)
        self.assertEqual(custom_game.max_attempts, 4)
        self.assertEqual(len(custom_game.secret_word), 6)
        self.assertEqual(len(custom_game.grid_labels), 4)
        self.assertEqual(len(custom_game.grid_labels[0]), 6)
        custom_game.unbind_events()
        custom_game.destroy()

    def test_guess_evaluation(self):
        secret = "APPLE"
        # Test exact match
        eval_exact = self.game.evaluate_guess("APPLE", secret)
        self.assertEqual(eval_exact, [COLOR_CORRECT] * 5)

        # Test partial match
        # Secret: A P P L E
        # Guess:  A L E R T
        eval_part = self.game.evaluate_guess("ALERT", secret)
        self.assertEqual(eval_part[0], COLOR_CORRECT)  # 'A' correct
        self.assertEqual(eval_part[1], COLOR_PRESENT)  # 'L' in secret
        self.assertEqual(eval_part[2], COLOR_PRESENT)  # 'E' in secret
        self.assertEqual(eval_part[3], COLOR_ABSENT)   # 'R' not in secret
        self.assertEqual(eval_part[4], COLOR_ABSENT)   # 'T' not in secret

    def test_input_handling(self):
        self.game.secret_word = "APPLE"
        for char in "APP":
            self.game.process_input(char)
        self.assertEqual(self.game.current_guess, "APP")

        # Backspace
        self.game.process_input("BACKSPACE")
        self.assertEqual(self.game.current_guess, "AP")

        # Exceed word length
        for char in "PLEExtra":
            self.game.process_input(char)
        self.assertEqual(self.game.current_guess, "APPLE")

    def test_win_condition(self):
        self.game.secret_word = "APPLE"
        self.game.current_guess = "APPLE"
        self.game.process_input("ENTER")

        self.assertTrue(self.game.game_won)
        self.assertTrue(self.game.game_over)
        self.assertEqual(len(self.game.attempts), 1)

    def test_loss_condition(self):
        self.game.word_length = 5
        self.game.max_attempts = 2
        self.game.reset_game()
        self.game.secret_word = "APPLE"

        # Attempt 1
        self.game.current_guess = "WRONG"
        self.game.process_input("ENTER")
        self.assertFalse(self.game.game_over)

        # Attempt 2
        self.game.current_guess = "WRONG"
        self.game.process_input("ENTER")
        self.assertTrue(self.game.game_over)
        self.assertFalse(self.game.game_won)

    def test_apply_custom_settings(self):
        self.game.length_var.set(7)
        self.game.attempts_var.set(8)
        self.game.apply_custom_settings()

        self.assertEqual(self.game.word_length, 7)
        self.assertEqual(self.game.max_attempts, 8)
        self.assertEqual(len(self.game.secret_word), 7)
        self.assertEqual(len(self.game.grid_labels), 8)


if __name__ == "__main__":
    unittest.main()
