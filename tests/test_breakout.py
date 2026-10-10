import unittest
import tkinter as tk
from games.breakout import BreakoutGame, CANVAS_WIDTH, CANVAS_HEIGHT, PADDLE_WIDTH, BALL_RADIUS


class TestBreakoutGame(unittest.TestCase):
    def setUp(self):
        self.root = tk.Tk()
        self.root.withdraw()
        self.game = BreakoutGame(self.root)

    def tearDown(self):
        if self.game.timer_id:
            self.game.after_cancel(self.game.timer_id)
        self.game.destroy()
        self.root.destroy()

    def test_initialization(self):
        self.assertEqual(self.game.score, 0)
        self.assertEqual(self.game.lives, 3)
        self.assertFalse(self.game.game_over)
        self.assertFalse(self.game.game_won)
        self.assertTrue(len(self.game.bricks) > 0)

    def test_paddle_movement(self):
        initial_x = self.game.paddle_x
        self.game.move_paddle(20)
        self.assertEqual(self.game.paddle_x, initial_x + 20)

        # Boundary check left
        self.game.move_paddle(-1000)
        self.assertEqual(self.game.paddle_x, 0)

        # Boundary check right
        self.game.move_paddle(1000)
        self.assertEqual(self.game.paddle_x, CANVAS_WIDTH - PADDLE_WIDTH)

    def test_wall_bounce(self):
        # Ball hits left wall
        self.game.ball_x = BALL_RADIUS
        self.game.ball_y = 100
        self.game.ball_dx = -4
        self.game.ball_dy = -4

        self.game.update_state()
        self.assertTrue(self.game.ball_dx > 0)

    def test_paddle_bounce(self):
        # Position ball right above paddle center
        self.game.ball_x = self.game.paddle_x + PADDLE_WIDTH / 2
        self.game.ball_y = self.game.paddle_y - BALL_RADIUS
        self.game.ball_dx = 0
        self.game.ball_dy = 4

        self.game.update_state()
        self.assertTrue(self.game.ball_dy < 0)

    def test_life_lost(self):
        # Ball moves past bottom wall
        self.game.ball_x = CANVAS_WIDTH / 2
        self.game.ball_y = CANVAS_HEIGHT - BALL_RADIUS + 10
        self.game.ball_dy = 4

        initial_lives = self.game.lives
        self.game.update_state()
        self.assertEqual(self.game.lives, initial_lives - 1)

    def test_brick_hit(self):
        # Find active brick
        brick = self.game.bricks[0]
        self.game.ball_x = (brick["x1"] + brick["x2"]) / 2
        self.game.ball_y = brick["y2"] + BALL_RADIUS - 1
        self.game.ball_dx = 0
        self.game.ball_dy = -4

        self.game.update_state()
        self.assertFalse(brick["active"])
        self.assertTrue(self.game.score > 0)

    def test_reset(self):
        self.game.lives = 1
        self.game.score = 100
        self.game.reset_game()

        self.assertEqual(self.game.lives, 3)
        self.assertEqual(self.game.score, 0)
        self.assertFalse(self.game.game_over)


if __name__ == "__main__":
    unittest.main()
