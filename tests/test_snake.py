import unittest
import tkinter as tk
from games.snake import SnakeGame, UP, DOWN, LEFT, RIGHT, GRID_SIZE


class TestSnakeGame(unittest.TestCase):
    def setUp(self):
        self.root = tk.Tk()
        self.root.withdraw()  # Hide window during test
        self.game = SnakeGame(self.root)

    def tearDown(self):
        if self.game.timer_id:
            self.game.after_cancel(self.game.timer_id)
        self.game.destroy()
        self.root.destroy()

    def test_initialization(self):
        self.assertEqual(self.game.score, 0)
        self.assertFalse(self.game.game_over)
        self.assertEqual(len(self.game.snake), 3)
        self.assertIsNotNone(self.game.food)

    def test_direction_change(self):
        self.game.direction = RIGHT
        self.game.change_direction(UP)
        self.assertEqual(self.game.next_direction, UP)

        # 180 turn should be ignored
        self.game.change_direction(DOWN)
        self.assertEqual(self.game.next_direction, UP)

    def test_movement_and_food_eat(self):
        initial_head = self.game.snake[0]
        # Place food right in front of snake
        self.game.direction = RIGHT
        self.game.next_direction = RIGHT
        target_food = (initial_head[0] + 1, initial_head[1])
        self.game.food = target_food

        self.game.update_state()

        self.assertEqual(self.game.snake[0], target_food)
        self.assertEqual(self.game.score, 10)
        self.assertEqual(len(self.game.snake), 4)

    def test_wall_collision(self):
        self.game.snake = [(GRID_SIZE - 1, 0), (GRID_SIZE - 2, 0), (GRID_SIZE - 3, 0)]
        self.game.direction = RIGHT
        self.game.next_direction = RIGHT

        self.game.update_state()
        self.assertTrue(self.game.game_over)

    def test_self_collision(self):
        # Snake in a loop
        self.game.snake = [(2, 2), (2, 3), (1, 3), (1, 2), (1, 1)]
        self.game.direction = LEFT
        self.game.next_direction = LEFT

        self.game.update_state()
        self.assertTrue(self.game.game_over)

    def test_reset(self):
        self.game.game_over = True
        self.game.score = 50
        self.game.reset_game()

        self.assertFalse(self.game.game_over)
        self.assertEqual(self.game.score, 0)
        self.assertEqual(len(self.game.snake), 3)


if __name__ == "__main__":
    unittest.main()
