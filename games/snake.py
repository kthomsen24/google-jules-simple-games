import random
import tkinter as tk

GRID_SIZE = 20
CELL_SIZE = 20
WIDTH = GRID_SIZE * CELL_SIZE
HEIGHT = GRID_SIZE * CELL_SIZE
INITIAL_SPEED = 120  # milliseconds delay per tick

UP = (0, -1)
DOWN = (0, 1)
LEFT = (-1, 0)
RIGHT = (1, 0)


class SnakeGame(tk.Frame):
    def __init__(self, parent, return_to_menu_callback=None):
        super().__init__(parent)
        self.parent = parent
        self.return_to_menu_callback = return_to_menu_callback

        self.score = 0
        self.direction = RIGHT
        self.next_direction = RIGHT
        self.game_over = False
        self.running = False
        self.timer_id = None

        self.snake = [(5, 5), (4, 5), (3, 5)]
        self.food = None

        self.setup_ui()
        self.spawn_food()
        self.bind_events()
        self.start_game()

    def setup_ui(self):
        self.pack(fill=tk.BOTH, expand=True)

        # Header / Status bar
        self.status_frame = tk.Frame(self, bg="#2c3e50")
        self.status_frame.pack(fill=tk.X, side=tk.TOP)

        self.score_label = tk.Label(
            self.status_frame,
            text=f"Score: {self.score}",
            font=("Helvetica", 14, "bold"),
            fg="#ecf0f1",
            bg="#2c3e50",
            padx=10,
            pady=5,
        )
        self.score_label.pack(side=tk.LEFT)

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
            self, width=WIDTH, height=HEIGHT, bg="#1a252f", highlightthickness=0
        )
        self.canvas.pack(padx=20, pady=20)

    def bind_events(self):
        self.parent.bind("<Up>", lambda e: self.change_direction(UP))
        self.parent.bind("<Down>", lambda e: self.change_direction(DOWN))
        self.parent.bind("<Left>", lambda e: self.change_direction(LEFT))
        self.parent.bind("<Right>", lambda e: self.change_direction(RIGHT))
        self.parent.bind("w", lambda e: self.change_direction(UP))
        self.parent.bind("s", lambda e: self.change_direction(DOWN))
        self.parent.bind("a", lambda e: self.change_direction(LEFT))
        self.parent.bind("d", lambda e: self.change_direction(RIGHT))

    def unbind_events(self):
        for key in ["<Up>", "<Down>", "<Left>", "<Right>", "w", "s", "a", "d"]:
            self.parent.unbind(key)

    def change_direction(self, new_dir):
        # Prevent 180 degree turns
        if (new_dir[0] + self.next_direction[0] != 0) or (new_dir[1] + self.next_direction[1] != 0):
            self.next_direction = new_dir

    def spawn_food(self):
        available = [
            (x, y)
            for x in range(GRID_SIZE)
            for y in range(GRID_SIZE)
            if (x, y) not in self.snake
        ]
        if available:
            self.food = random.choice(available)
        else:
            self.food = None

    def start_game(self):
        self.running = True
        self.game_loop()

    def reset_game(self):
        if self.timer_id:
            self.after_cancel(self.timer_id)
            self.timer_id = None
        self.score = 0
        self.score_label.config(text=f"Score: {self.score}")
        self.direction = RIGHT
        self.next_direction = RIGHT
        self.game_over = False
        self.snake = [(5, 5), (4, 5), (3, 5)]
        self.spawn_food()
        self.start_game()

    def game_loop(self):
        if not self.running:
            return

        self.update_state()
        self.draw()

        if not self.game_over:
            self.timer_id = self.after(INITIAL_SPEED, self.game_loop)

    def update_state(self):
        if self.game_over:
            return

        self.direction = self.next_direction
        head_x, head_y = self.snake[0]
        dx, dy = self.direction
        new_head = (head_x + dx, head_y + dy)

        # Check collision with walls
        if not (0 <= new_head[0] < GRID_SIZE and 0 <= new_head[1] < GRID_SIZE):
            self.game_over = True
            return

        # Check collision with self
        if new_head in self.snake:
            self.game_over = True
            return

        self.snake.insert(0, new_head)

        # Check food collision
        if new_head == self.food:
            self.score += 10
            self.score_label.config(text=f"Score: {self.score}")
            self.spawn_food()
        else:
            self.snake.pop()

    def draw(self):
        self.canvas.delete("all")

        # Draw grid subtle lines
        for x in range(0, WIDTH, CELL_SIZE):
            self.canvas.create_line(x, 0, x, HEIGHT, fill="#243342")
        for y in range(0, HEIGHT, CELL_SIZE):
            self.canvas.create_line(0, y, WIDTH, y, fill="#243342")

        # Draw Food
        if self.food:
            fx, fy = self.food
            x1 = fx * CELL_SIZE + 2
            y1 = fy * CELL_SIZE + 2
            x2 = (fx + 1) * CELL_SIZE - 2
            y2 = (fy + 1) * CELL_SIZE - 2
            self.canvas.create_oval(x1, y1, x2, y2, fill="#e74c3c", outline="#c0392b")

        # Draw Snake
        for idx, (sx, sy) in enumerate(self.snake):
            x1 = sx * CELL_SIZE + 1
            y1 = sy * CELL_SIZE + 1
            x2 = (sx + 1) * CELL_SIZE - 1
            y2 = (sy + 1) * CELL_SIZE - 1
            color = "#2ecc71" if idx == 0 else "#27ae60"
            self.canvas.create_rectangle(x1, y1, x2, y2, fill=color, outline="#1e8449")

        # Draw Game Over overlay
        if self.game_over:
            self.canvas.create_rectangle(
                40, HEIGHT // 2 - 40, WIDTH - 40, HEIGHT // 2 + 40,
                fill="#000000"
            )
            self.canvas.create_text(
                WIDTH // 2,
                HEIGHT // 2 - 10,
                text="GAME OVER",
                fill="#e74c3c",
                font=("Helvetica", 22, "bold"),
            )
            self.canvas.create_text(
                WIDTH // 2,
                HEIGHT // 2 + 20,
                text="Click Restart to play again",
                fill="#ecf0f1",
                font=("Helvetica", 11),
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
    root.title("Snake Game")
    root.geometry("450x520")
    game = SnakeGame(root)
    root.mainloop()
