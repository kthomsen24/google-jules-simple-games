import tkinter as tk
from games.snake import SnakeGame
from games.breakout import BreakoutGame
from games.wordle import WordleGame
from games.six_degrees import SixDegreesGame


class GameLauncher(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Game Center - Select a Game")
        self.geometry("560x700")
        self.configure(bg="#1a252f")
        self.resizable(False, False)

        self.current_frame = None
        self.show_menu()

    def show_menu(self):
        if self.current_frame:
            self.current_frame.destroy()

        self.current_frame = tk.Frame(self, bg="#1a252f")
        self.current_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)

        # Title
        title_label = tk.Label(
            self.current_frame,
            text="Game Launcher",
            font=("Helvetica", 24, "bold"),
            fg="#ecf0f1",
            bg="#1a252f",
            pady=10,
        )
        title_label.pack()

        subtitle_label = tk.Label(
            self.current_frame,
            text="Select a game to start playing:",
            font=("Helvetica", 12),
            fg="#bdc3c7",
            bg="#1a252f",
            pady=5,
        )
        subtitle_label.pack()

        # Button Container
        btn_frame = tk.Frame(self.current_frame, bg="#1a252f")
        btn_frame.pack(expand=True)

        # Snake Game Button
        snake_btn = tk.Button(
            btn_frame,
            text="🐍 Play Snake",
            font=("Helvetica", 13, "bold"),
            bg="#2ecc71",
            fg="white",
            activebackground="#27ae60",
            activeforeground="white",
            relief=tk.RAISED,
            bd=3,
            width=24,
            height=2,
            command=self.start_snake,
            cursor="hand2",
        )
        snake_btn.pack(pady=8)

        # Breakout Game Button
        breakout_btn = tk.Button(
            btn_frame,
            text="🧱 Play Breakout",
            font=("Helvetica", 13, "bold"),
            bg="#e74c3c",
            fg="white",
            activebackground="#c0392b",
            activeforeground="white",
            relief=tk.RAISED,
            bd=3,
            width=24,
            height=2,
            command=self.start_breakout,
            cursor="hand2",
        )
        breakout_btn.pack(pady=8)

        # Wordle Game Button
        wordle_btn = tk.Button(
            btn_frame,
            text="🔤 Play Wordle",
            font=("Helvetica", 13, "bold"),
            bg="#f39c12",
            fg="white",
            activebackground="#d35400",
            activeforeground="white",
            relief=tk.RAISED,
            bd=3,
            width=24,
            height=2,
            command=self.start_wordle,
            cursor="hand2",
        )
        wordle_btn.pack(pady=8)

        # Six Degrees of Wikipedia Button
        six_degrees_btn = tk.Button(
            btn_frame,
            text="🌐 Six Degrees of Wikipedia",
            font=("Helvetica", 13, "bold"),
            bg="#9b59b6",
            fg="white",
            activebackground="#8e44ad",
            activeforeground="white",
            relief=tk.RAISED,
            bd=3,
            width=24,
            height=2,
            command=self.start_six_degrees,
            cursor="hand2",
        )
        six_degrees_btn.pack(pady=8)

        # Footer
        footer_label = tk.Label(
            self.current_frame,
            text="Select an option above to launch",
            font=("Helvetica", 9, "italic"),
            fg="#7f8c8d",
            bg="#1a252f",
            pady=10,
        )
        footer_label.pack(side=tk.BOTTOM)

    def start_snake(self):
        if self.current_frame:
            self.current_frame.destroy()
        self.title("Game Center - Snake")
        self.current_frame = SnakeGame(self, return_to_menu_callback=self.show_menu)

    def start_breakout(self):
        if self.current_frame:
            self.current_frame.destroy()
        self.title("Game Center - Breakout")
        self.current_frame = BreakoutGame(self, return_to_menu_callback=self.show_menu)

    def start_wordle(self):
        if self.current_frame:
            self.current_frame.destroy()
        self.title("Game Center - Wordle")
        self.current_frame = WordleGame(self, return_to_menu_callback=self.show_menu)

    def start_six_degrees(self):
        if self.current_frame:
            self.current_frame.destroy()
        self.title("Game Center - Six Degrees of Wikipedia")
        self.current_frame = SixDegreesGame(self, return_to_menu_callback=self.show_menu)


if __name__ == "__main__":
    app = GameLauncher()
    app.mainloop()
