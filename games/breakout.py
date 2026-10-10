import tkinter as tk

CANVAS_WIDTH = 480
CANVAS_HEIGHT = 400
PADDLE_WIDTH = 80
PADDLE_HEIGHT = 12
PADDLE_SPEED = 20
BALL_RADIUS = 7
TICK_MS = 16  # ~60 FPS

BRICK_ROWS = 5
BRICK_COLS = 8
BRICK_HEIGHT = 18
BRICK_PADDING = 4
BRICK_OFFSET_TOP = 40
BRICK_OFFSET_LEFT = 10

BRICK_COLORS = ["#e74c3c", "#e67e22", "#f1c40f", "#2ecc71", "#3498db"]


class BreakoutGame(tk.Frame):
    def __init__(self, parent, return_to_menu_callback=None):
        super().__init__(parent)
        self.parent = parent
        self.return_to_menu_callback = return_to_menu_callback

        self.score = 0
        self.lives = 3
        self.game_over = False
        self.game_won = False
        self.running = False
        self.timer_id = None

        self.paddle_x = (CANVAS_WIDTH - PADDLE_WIDTH) / 2
        self.paddle_y = CANVAS_HEIGHT - 30

        self.ball_x = CANVAS_WIDTH / 2
        self.ball_y = self.paddle_y - BALL_RADIUS - 2
        self.ball_dx = 4
        self.ball_dy = -4

        self.bricks = []  # List of dicts with rect coordinates and state
        self.setup_bricks()

        self.setup_ui()
        self.bind_events()
        self.start_game()

    def setup_bricks(self):
        self.bricks = []
        brick_width = (CANVAS_WIDTH - 2 * BRICK_OFFSET_LEFT - (BRICK_COLS - 1) * BRICK_PADDING) / BRICK_COLS

        for r in range(BRICK_ROWS):
            for c in range(BRICK_COLS):
                x1 = BRICK_OFFSET_LEFT + c * (brick_width + BRICK_PADDING)
                y1 = BRICK_OFFSET_TOP + r * (BRICK_HEIGHT + BRICK_PADDING)
                x2 = x1 + brick_width
                y2 = y1 + BRICK_HEIGHT
                color = BRICK_COLORS[r % len(BRICK_COLORS)]
                self.bricks.append({
                    "x1": x1, "y1": y1, "x2": x2, "y2": y2,
                    "color": color, "active": True,
                    "points": (BRICK_ROWS - r) * 10
                })

    def setup_ui(self):
        self.pack(fill=tk.BOTH, expand=True)

        # Header / Status bar
        self.status_frame = tk.Frame(self, bg="#2c3e50")
        self.status_frame.pack(fill=tk.X, side=tk.TOP)

        self.score_label = tk.Label(
            self.status_frame,
            text=f"Score: {self.score}",
            font=("Helvetica", 12, "bold"),
            fg="#ecf0f1",
            bg="#2c3e50",
            padx=10,
            pady=5,
        )
        self.score_label.pack(side=tk.LEFT)

        self.lives_label = tk.Label(
            self.status_frame,
            text=f"Lives: {self.lives}",
            font=("Helvetica", 12, "bold"),
            fg="#e74c3c",
            bg="#2c3e50",
            padx=10,
            pady=5,
        )
        self.lives_label.pack(side=tk.LEFT)

        if self.return_to_menu_callback:
            self.back_btn = tk.Button(
                self.status_frame,
                text="Main Menu",
                command=self.return_to_menu,
                bg="#e74c3c",
                fg="white",
                font=("Helvetica", 10, "bold"),
                relief=tk.FLAT,
                padx=8,
            )
            self.back_btn.pack(side=tk.RIGHT, padx=10, pady=5)

        self.restart_btn = tk.Button(
            self.status_frame,
            text="Restart",
            command=self.reset_game,
            bg="#3498db",
            fg="white",
            font=("Helvetica", 10, "bold"),
            relief=tk.FLAT,
            padx=8,
        )
        self.restart_btn.pack(side=tk.RIGHT, padx=5, pady=5)

        # Game Canvas
        self.canvas = tk.Canvas(
            self, width=CANVAS_WIDTH, height=CANVAS_HEIGHT, bg="#1a252f", highlightthickness=0
        )
        self.canvas.pack(padx=20, pady=20)

    def bind_events(self):
        self.parent.bind("<Left>", lambda e: self.move_paddle(-PADDLE_SPEED))
        self.parent.bind("<Right>", lambda e: self.move_paddle(PADDLE_SPEED))
        self.parent.bind("a", lambda e: self.move_paddle(-PADDLE_SPEED))
        self.parent.bind("d", lambda e: self.move_paddle(PADDLE_SPEED))
        self.canvas.bind("<Motion>", self.mouse_move_paddle)

    def unbind_events(self):
        for key in ["<Left>", "<Right>", "a", "d"]:
            self.parent.unbind(key)
        self.canvas.unbind("<Motion>")

    def move_paddle(self, dx):
        self.paddle_x = max(0, min(CANVAS_WIDTH - PADDLE_WIDTH, self.paddle_x + dx))

    def mouse_move_paddle(self, event):
        self.paddle_x = max(0, min(CANVAS_WIDTH - PADDLE_WIDTH, event.x - PADDLE_WIDTH / 2))

    def start_game(self):
        self.running = True
        self.game_loop()

    def reset_game(self):
        if self.timer_id:
            self.after_cancel(self.timer_id)
            self.timer_id = None
        self.score = 0
        self.lives = 3
        self.score_label.config(text=f"Score: {self.score}")
        self.lives_label.config(text=f"Lives: {self.lives}")
        self.game_over = False
        self.game_won = False
        self.paddle_x = (CANVAS_WIDTH - PADDLE_WIDTH) / 2
        self.reset_ball()
        self.setup_bricks()
        self.start_game()

    def reset_ball(self):
        self.ball_x = CANVAS_WIDTH / 2
        self.ball_y = self.paddle_y - BALL_RADIUS - 2
        self.ball_dx = 4
        self.ball_dy = -4

    def game_loop(self):
        if not self.running:
            return

        self.update_state()
        self.draw()

        if not self.game_over and not self.game_won:
            self.timer_id = self.after(TICK_MS, self.game_loop)

    def update_state(self):
        if self.game_over or self.game_won:
            return

        # Move ball
        new_bx = self.ball_x + self.ball_dx
        new_by = self.ball_y + self.ball_dy

        # Wall collisions (Left/Right)
        if new_bx - BALL_RADIUS <= 0:
            new_bx = BALL_RADIUS
            self.ball_dx = abs(self.ball_dx)
        elif new_bx + BALL_RADIUS >= CANVAS_WIDTH:
            new_bx = CANVAS_WIDTH - BALL_RADIUS
            self.ball_dx = -abs(self.ball_dx)

        # Top collision
        if new_by - BALL_RADIUS <= 0:
            new_by = BALL_RADIUS
            self.ball_dy = abs(self.ball_dy)

        # Bottom collision (Life lost)
        if new_by + BALL_RADIUS >= CANVAS_HEIGHT:
            self.lives -= 1
            self.lives_label.config(text=f"Lives: {self.lives}")
            if self.lives <= 0:
                self.game_over = True
                return
            else:
                self.reset_ball()
                return

        # Paddle collision
        paddle_left = self.paddle_x
        paddle_right = self.paddle_x + PADDLE_WIDTH
        paddle_top = self.paddle_y
        paddle_bottom = self.paddle_y + PADDLE_HEIGHT

        if (paddle_top <= new_by + BALL_RADIUS <= paddle_bottom) and (
            paddle_left <= new_bx <= paddle_right
        ) and self.ball_dy > 0:
            self.ball_dy = -abs(self.ball_dy)
            # Adjust dx based on hit position relative to paddle center
            hit_pos = (new_bx - (paddle_left + PADDLE_WIDTH / 2)) / (PADDLE_WIDTH / 2)
            self.ball_dx = hit_pos * 6  # max horizontal speed factor

        # Brick collisions
        for brick in self.bricks:
            if not brick["active"]:
                continue

            bx1, by1, bx2, by2 = brick["x1"], brick["y1"], brick["x2"], brick["y2"]
            if (bx1 <= new_bx <= bx2 or bx1 <= new_bx - BALL_RADIUS <= bx2 or bx1 <= new_bx + BALL_RADIUS <= bx2) and \
               (by1 <= new_by <= by2 or by1 <= new_by - BALL_RADIUS <= by2 or by1 <= new_by + BALL_RADIUS <= by2):
                brick["active"] = False
                self.score += brick["points"]
                self.score_label.config(text=f"Score: {self.score}")
                self.ball_dy = -self.ball_dy
                break

        # Check win condition
        if all(not b["active"] for b in self.bricks):
            self.game_won = True

        self.ball_x = new_bx
        self.ball_y = new_by

    def draw(self):
        self.canvas.delete("all")

        # Draw Bricks
        for brick in self.bricks:
            if brick["active"]:
                self.canvas.create_rectangle(
                    brick["x1"], brick["y1"], brick["x2"], brick["y2"],
                    fill=brick["color"], outline="#2c3e50"
                )

        # Draw Paddle
        self.canvas.create_rectangle(
            self.paddle_x, self.paddle_y,
            self.paddle_x + PADDLE_WIDTH, self.paddle_y + PADDLE_HEIGHT,
            fill="#ecf0f1", outline="#bdc3c7"
        )

        # Draw Ball
        self.canvas.create_oval(
            self.ball_x - BALL_RADIUS, self.ball_y - BALL_RADIUS,
            self.ball_x + BALL_RADIUS, self.ball_y + BALL_RADIUS,
            fill="#e74c3c", outline="#c0392b"
        )

        # Draw Game Over or Victory message
        if self.game_over:
            self.canvas.create_text(
                CANVAS_WIDTH // 2, CANVAS_HEIGHT // 2,
                text="GAME OVER", fill="#e74c3c", font=("Helvetica", 22, "bold")
            )
            self.canvas.create_text(
                CANVAS_WIDTH // 2, CANVAS_HEIGHT // 2 + 30,
                text="Click Restart to play again", fill="#ecf0f1", font=("Helvetica", 11)
            )
        elif self.game_won:
            self.canvas.create_text(
                CANVAS_WIDTH // 2, CANVAS_HEIGHT // 2,
                text="YOU WIN!", fill="#2ecc71", font=("Helvetica", 22, "bold")
            )
            self.canvas.create_text(
                CANVAS_WIDTH // 2, CANVAS_HEIGHT // 2 + 30,
                text="Click Restart to play again", fill="#ecf0f1", font=("Helvetica", 11)
            )

    def return_to_menu(self):
        if self.timer_id:
            self.after_cancel(self.timer_id)
            self.timer_id = None
        self.running = False
        self.unbind_events()
        self.destroy()
        if self.return_to_menu_callback:
            self.return_to_menu_callback()


if __name__ == "__main__":
    root = tk.Tk()
    root.title("Breakout / Arkanoid")
    root.geometry("520x500")
    game = BreakoutGame(root)
    root.mainloop()
