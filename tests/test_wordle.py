import unittest
import tkinter as tk
from games.wordle import WordleGame, COLOR_CORRECT, COLOR_PRESENT, COLOR_ABSENT, COLOR_TEXT, COLOR_TEXT_MORE_INSTANCES, DEFAULT_WORD_LENGTH, DEFAULT_MAX_ATTEMPTS
from games.wordle_dictionary import LARGE_WORD_DICTIONARY


class TestWordleGame(unittest.TestCase):
    def setUp(self):
        self.root = tk.Tk()
        self.root.withdraw()
        self.game = WordleGame(self.root, show_dialogs=False)

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

    def test_expanded_word_lengths_four_to_ten(self):
        # Test word lengths 4 to 10
        for length in [4, 5, 6, 7, 8, 9, 10]:
            custom_game = WordleGame(self.root, word_length=length, max_attempts=6, show_dialogs=False)
            self.assertEqual(custom_game.word_length, length)
            self.assertEqual(len(custom_game.secret_word), length)
            dict_list = LARGE_WORD_DICTIONARY.get(length) or LARGE_WORD_DICTIONARY.get(str(length))
            self.assertIn(custom_game.secret_word, dict_list)
            custom_game.unbind_events()
            custom_game.destroy()

    def test_reject_invalid_word_length(self):
        self.game.length_var.set(3)
        self.game.apply_custom_settings()
        self.assertIn("Invalid Word Length", self.game.msg_banner.cget("text"))

        self.game.length_var.set(11)
        self.game.apply_custom_settings()
        self.assertIn("Invalid Word Length", self.game.msg_banner.cget("text"))

    def test_non_dictionary_guess_rejected(self):
        self.game.word_length = 5
        self.game.reset_game()
        initial_attempts = len(self.game.attempts)

        # Enter bogus guess "ZZZZZ"
        for char in "ZZZZZ":
            self.game.process_input(char)
        self.game.process_input("ENTER")

        # Guess should NOT be accepted, attempts count should remain unchanged
        self.assertEqual(len(self.game.attempts), initial_attempts)
        self.assertIn("not in the internal word list", self.game.msg_banner.cget("text"))

    def test_valid_dictionary_guess_accepted(self):
        self.game.word_length = 5
        self.game.reset_game()
        valid_guess = self.game.get_word_dictionary_for_length(5)[0]

        for char in valid_guess:
            self.game.process_input(char)
        self.game.process_input("ENTER")

        self.assertEqual(len(self.game.attempts), 1)
        self.assertEqual(self.game.attempts[0], valid_guess)

    def test_blue_text_color_for_more_letter_instances(self):
        custom_game = WordleGame(self.root, word_length=4, max_attempts=6, show_dialogs=False)
        # Choose valid solution in dictionary with repeating letter: "COOL"
        custom_game.secret_word = "COOL"
        # Enter valid dictionary guess "CODE"
        for char in "CODE":
            custom_game.process_input(char)
        custom_game.process_input("ENTER")

        # 'C', 'O' match in position/presence
        # 'O' in "COOL" has 2 instances vs 1 instance in "CODE" -> blue text color
        self.assertEqual(custom_game.grid_labels[0][1].cget("fg"), COLOR_TEXT_MORE_INSTANCES)

        custom_game.unbind_events()
        custom_game.destroy()

    def test_session_history_and_duplicate_avoidance(self):
        # Reset game multiple times in same session
        used_words = set()
        for _ in range(5):
            word = self.game.secret_word
            self.assertNotIn(word, used_words)
            used_words.add(word)
            self.game.reset_game()

        self.assertEqual(len(self.game.used_solutions), 6)

    def test_guess_evaluation(self):
        secret = "APPLE"
        eval_exact = self.game.evaluate_guess("APPLE", secret)
        self.assertEqual(eval_exact, [COLOR_CORRECT] * 5)

        eval_part = self.game.evaluate_guess("ALERT", secret)
        self.assertEqual(eval_part[0], COLOR_CORRECT)
        self.assertEqual(eval_part[1], COLOR_PRESENT)
        self.assertEqual(eval_part[2], COLOR_PRESENT)
        self.assertEqual(eval_part[3], COLOR_ABSENT)
        self.assertEqual(eval_part[4], COLOR_ABSENT)

    def test_input_handling(self):
        self.game.secret_word = "APPLE"
        for char in "APP":
            self.game.process_input(char)
        self.assertEqual(self.game.current_guess, "APP")

        # Backspace
        self.game.process_input("BACKSPACE")
        self.assertEqual(self.game.current_guess, "AP")

    def test_out_of_order_slot_insertion(self):
        self.game.secret_word = "APPLE"
        self.game.on_slot_click(0, 3)
        self.assertEqual(self.game.selected_slot, 3)

        self.game.process_input("L")
        self.assertEqual(self.game.current_guess_slots, ["", "", "", "L", ""])
        self.assertIsNone(self.game.selected_slot)
        self.assertTrue(self.game.manual_insertion_done)

    def test_win_condition(self):
        self.game.secret_word = "APPLE"
        for char in "APPLE":
            self.game.process_input(char)
        self.game.process_input("ENTER")

        self.assertTrue(self.game.game_won)
        self.assertTrue(self.game.game_over)

    def test_loss_condition(self):
        self.game.word_length = 5
        self.game.max_attempts = 2
        self.game.reset_game()
        self.game.secret_word = "APPLE"

        valid_words = self.game.get_word_dictionary_for_length(5)
        wrong_word = [w for w in valid_words if w != "APPLE"][0]

        # Attempt 1
        for char in wrong_word:
            self.game.process_input(char)
        self.game.process_input("ENTER")
        self.assertFalse(self.game.game_over)

        # Attempt 2
        for char in wrong_word:
            self.game.process_input(char)
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
