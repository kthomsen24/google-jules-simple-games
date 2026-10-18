import unittest
import tkinter as tk
from games.six_degrees import SixDegreesGame, FALLBACK_GRAPH, fetch_opening_links


class TestSixDegreesGame(unittest.TestCase):
    def setUp(self):
        self.root = tk.Tk()
        self.root.withdraw()
        self.game = SixDegreesGame(self.root, use_network=False, show_dialogs=False)

    def tearDown(self):
        self.game.destroy()
        self.root.destroy()

    def test_initialization(self):
        self.assertTrue(self.game.random_start)
        self.assertEqual(self.game.chain_length, 6)
        self.assertEqual(self.game.max_attempts, 6)
        self.assertFalse(self.game.infinite_attempts)
        self.assertIsNotNone(self.game.start_page)
        self.assertIsNotNone(self.game.target_page)
        self.assertEqual(len(self.game.chain), 1)

    def test_fetch_opening_links_offline(self):
        title, links = fetch_opening_links("Python (programming language)", use_network=False)
        self.assertEqual(title, "Python (programming language)")
        self.assertTrue(len(links) > 0)
        self.assertIn("Guido van Rossum", links)

    def test_follow_link_and_chain_building(self):
        self.game.start_page = "Python (programming language)"
        self.game.target_page = "Netherlands"
        self.game.chain = ["Python (programming language)"]
        self.game.attempts_used = 0
        self.game.update_game_state()

        # Select first link ("Guido van Rossum")
        self.game.links_listbox.selection_clear(0, tk.END)
        self.game.links_listbox.selection_set(0)
        self.game.follow_selected_link()

        self.assertEqual(self.game.attempts_used, 1)
        self.assertEqual(len(self.game.chain), 2)
        self.assertEqual(self.game.chain[-1], "Guido van Rossum")
        self.assertIn("Chain Length: 1 / Max: 6", self.game.chain_count_label.cget("text"))

    def test_undo_step_decrements_attempts(self):
        self.game.chain = ["Python (programming language)", "Guido van Rossum"]
        self.game.attempts_used = 1
        self.game.update_game_state()

        self.game.undo_step()
        self.assertEqual(len(self.game.chain), 1)
        self.assertEqual(self.game.attempts_used, 0)
        self.assertEqual(self.game.chain[0], "Python (programming language)")
        self.assertIn("Chain Length: 0 / Max: 6", self.game.chain_count_label.cget("text"))

    def test_link_list_sorting(self):
        self.game.chain = ["Python (programming language)"]
        self.game.update_game_state()

        # Check default article order
        article_order_list = list(self.game.links_listbox.get(0, tk.END))

        # Test Alphabetical (A-Z)
        self.game.on_sort_change("Alphabetical (A-Z)")
        az_list = list(self.game.links_listbox.get(0, tk.END))
        self.assertEqual(az_list, sorted(article_order_list))

        # Test Alphabetical (Z-A)
        self.game.on_sort_change("Alphabetical (Z-A)")
        za_list = list(self.game.links_listbox.get(0, tk.END))
        self.assertEqual(za_list, sorted(article_order_list, reverse=True))

        # Return to Article Order
        self.game.on_sort_change("Article Order")
        restored_list = list(self.game.links_listbox.get(0, tk.END))
        self.assertEqual(restored_list, article_order_list)

    def test_win_condition(self):
        self.game.start_page = "Python (programming language)"
        self.game.target_page = "Guido van Rossum"
        self.game.chain = ["Python (programming language)", "Guido van Rossum"]
        self.game.update_game_state()

        self.assertTrue(self.game.game_won)
        self.assertTrue(self.game.game_over)

    def test_max_attempts_exceeded(self):
        self.game.max_attempts = 2
        self.game.attempts_used = 2
        self.game.start_page = "Python (programming language)"
        self.game.target_page = "Earth"
        self.game.chain = ["Python (programming language)"]
        self.game.update_game_state()

        self.assertTrue(self.game.game_over)
        self.assertFalse(self.game.game_won)

    def test_infinite_attempts(self):
        self.game.infinite_attempts = True
        self.game.max_attempts = 2
        self.game.attempts_used = 5
        self.game.start_page = "Python (programming language)"
        self.game.target_page = "Earth"
        self.game.chain = ["Python (programming language)"]
        self.game.update_game_state()

        self.assertFalse(self.game.game_over)


if __name__ == "__main__":
    unittest.main()
