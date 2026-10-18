import hashlib
import random
import time
import tkinter as tk
from tkinter import messagebox
from games.wordle_dictionary import LARGE_WORD_DICTIONARY

# Default game parameters
DEFAULT_WORD_LENGTH = 5
DEFAULT_MAX_ATTEMPTS = 6

# Tile background colors according to Wordle feedback
COLOR_CORRECT = "#538d4e"    # Green
COLOR_PRESENT = "#b59f3b"    # Yellow
COLOR_ABSENT = "#3a3a3c"     # Dark Gray
COLOR_DEFAULT = "#121213"    # Dark background for empty/editing tiles
COLOR_BORDER = "#3a3a3c"     # Grid border color
COLOR_SELECTED = "#3498db"   # Border color for selected slot
COLOR_TEXT = "#ffffff"       # Standard text color
COLOR_TEXT_MORE_INSTANCES = "#3498db" # Blue text color when secret contains more instances of letter

# Simple fallback dictionary
FALLBACK_WORD_DICTIONARY = {
    4: ["WORD", "GAME", "PLAY", "CODE", "COOL", "FIRE", "BLUE", "STAR", "FISH", "MOON", "RAIN", "TIME", "MIND", "BEAR", "TREE"],
    5: ["APPLE", "BRAIN", "CHAIR", "DANCE", "EAGLE", "FLAME", "GRAPE", "HOUSE", "LIGHT", "MUSIC", "PLANT", "SNAKE", "TABLE", "WATER", "WORLD", "REACT", "SMART", "FLASH", "CLOUD", "PIANO"],
    6: ["BANANA", "CASTLE", "DRAGON", "FLOWER", "PLANET", "ROCKET", "SILVER", "SUMMER", "WINTER", "BRIDGE", "GUITAR", "PURPLE", "FOREST", "SPRING", "MONKEY"],
    7: ["ACADEMY", "DIAMOND", "KINGDOM", "MONSTER", "PICTURE", "RAINBOW", "SUNRISE", "FREEDOM", "CAPTAIN", "PERFECT", "JOURNEY", "SILENCE", "STUDENT", "WELCOME", "SUCCESS"],
    8: ["BUILDING", "COMPUTER", "ELEPHANT", "FOOTBALL", "MOUNTAIN", "SATELLITE", "SUNFLOWER", "TREASURE", "UNIVERSE", "BEAUTIFUL", "HOSPITAL", "LANGUAGE", "QUESTION", "STRENGTH", "TOGETHER"]
}


class WordleGame(tk.Frame):
    def __init__(self, parent, return_to_menu_callback=None, word_length=DEFAULT_WORD_LENGTH, max_attempts=DEFAULT_MAX_ATTEMPTS, show_dialogs=True):
        super().__init__(parent, bg="#121213")
        self.parent = parent
        self.return_to_menu_callback = return_to_menu_callback
        self.show_dialogs = show_dialogs

        self.word_length = max(4, min(10, word_length))
        self.max_attempts = max_attempts

        self.secret_word = ""
        self.attempts = []  # List of guessed words
        self.current_guess_slots = [""] * self.word_length
        self.selected_slot = None
        self.manual_insertion_done = False

        self.game_over = False
        self.game_won = False

        # Session history tracking solutions used in current session
        self.used_solutions = []

        # Virtual Keyboard key statuses: letter -> color
        self.key_status = {}

        self.setup_ui()
        self.reset_game()

    @property
    def current_guess(self):
        return "".join(self.current_guess_slots)

    @current_guess.setter
    def current_guess(self, value):
        self.current_guess_slots = [""] * self.word_length
        for i, char in enumerate(value[:self.word_length]):
            self.current_guess_slots[i] = char.upper()
        self.update_current_row_display()

    def get_word_dictionary_for_length(self, length):
        dict_list = LARGE_WORD_DICTIONARY.get(length) or LARGE_WORD_DICTIONARY.get(str(length))
        if not dict_list:
            dict_list = FALLBACK_WORD_DICTIONARY.get(length, FALLBACK_WORD_DICTIONARY[5])
        return [w.upper() for w in dict_list]

    def setup_ui(self):
        self.pack(fill=tk.BOTH, expand=True)

        # Header / Controls Frame
        self.header_frame = tk.Frame(self, bg="#2c3e50")
        self.header_frame.pack(fill=tk.X, side=tk.TOP)

        title_label = tk.Label(
            self.header_frame,
            text="WORDLE",
            font=("Helvetica", 16, "bold"),
            fg="#ecf0f1",
            bg="#2c3e50",
            padx=10,
            pady=5,
        )
        title_label.pack(side=tk.LEFT)

        if self.return_to_menu_callback:
            self.back_btn = tk.Button(
                self.header_frame,
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
            self.header_frame,
            text="Restart",
            command=self.reset_game,
            bg="#3498db",
            fg="white",
            font=("Helvetica", 10, "bold"),
            relief=tk.FLAT,
            padx=8,
        )
        self.restart_btn.pack(side=tk.RIGHT, padx=5, pady=5)

        # Customization Panel
        self.custom_frame = tk.Frame(self, bg="#121213")
        self.custom_frame.pack(fill=tk.X, pady=5)

        length_label = tk.Label(
            self.custom_frame,
            text="Word Length (4-10):",
            font=("Helvetica", 10, "bold"),
            fg="#ecf0f1",
            bg="#121213",
        )
        length_label.pack(side=tk.LEFT, padx=(15, 5))

        self.length_var = tk.IntVar(value=self.word_length)
        self.length_spin = tk.Spinbox(
            self.custom_frame,
            from_=4,
            to=10,
            textvariable=self.length_var,
            width=3,
            font=("Helvetica", 10),
            command=self.apply_custom_settings,
        )
        self.length_spin.pack(side=tk.LEFT, padx=(0, 15))

        attempts_label = tk.Label(
            self.custom_frame,
            text="Max Attempts:",
            font=("Helvetica", 10, "bold"),
            fg="#ecf0f1",
            bg="#121213",
        )
        attempts_label.pack(side=tk.LEFT, padx=(0, 5))

        self.attempts_var = tk.IntVar(value=self.max_attempts)
        self.attempts_spin = tk.Spinbox(
            self.custom_frame,
            from_=1,
            to=10,
            textvariable=self.attempts_var,
            width=3,
            font=("Helvetica", 10),
            command=self.apply_custom_settings,
        )
        self.attempts_spin.pack(side=tk.LEFT)

        self.apply_btn = tk.Button(
            self.custom_frame,
            text="Apply & New Game",
            command=self.apply_custom_settings,
            bg="#2ecc71",
            fg="white",
            font=("Helvetica", 9, "bold"),
            relief=tk.FLAT,
            padx=6,
            pady=2,
        )
        self.apply_btn.pack(side=tk.LEFT, padx=15)

        # Info & Hint Banners
        self.rule_label = tk.Label(
            self,
            text="ℹ️ Word lengths must be 4 to 10 letters. Guesses must be valid English words.",
            font=("Helvetica", 9),
            fg="#bdc3c7",
            bg="#121213",
            pady=1,
        )
        self.rule_label.pack()

        self.hint_label = tk.Label(
            self,
            text="💡 Blue font indicates the secret word contains more instances of that letter.",
            font=("Helvetica", 9, "italic"),
            fg="#3498db",
            bg="#121213",
            pady=1,
        )
        self.hint_label.pack()

        # Feedback/Error Banner
        self.msg_banner = tk.Label(
            self,
            text="",
            font=("Helvetica", 10, "bold"),
            fg="#e74c3c",
            bg="#121213",
            pady=2,
        )
        self.msg_banner.pack()

        # Grid Container
        self.grid_container = tk.Frame(self, bg="#121213")
        self.grid_container.pack(expand=True, pady=5)

        # Onscreen Keyboard Container
        self.keyboard_frame = tk.Frame(self, bg="#121213")
        self.keyboard_frame.pack(side=tk.BOTTOM, pady=10)

        self.bind_events()

    def bind_events(self):
        self.parent.bind("<Key>", self.handle_keypress)

    def unbind_events(self):
        self.parent.unbind("<Key>")

    def apply_custom_settings(self):
        try:
            length = int(self.length_var.get())
            attempts = int(self.attempts_var.get())
            if not (4 <= length <= 10):
                msg = f"Invalid Word Length ({length})! Only English words of 4 to 10 letters are supported."
                self.msg_banner.config(text=msg, fg="#e74c3c")
                if self.show_dialogs:
                    messagebox.showerror("Invalid Word Length", msg)
                return
            if not (1 <= attempts <= 10):
                msg = "Max attempts must be between 1 and 10."
                self.msg_banner.config(text=msg, fg="#e74c3c")
                if self.show_dialogs:
                    messagebox.showerror("Invalid Attempts", msg)
                return

            self.msg_banner.config(text="")
            self.word_length = length
            self.max_attempts = attempts
            self.reset_game()
        except ValueError:
            pass

    def select_secret_word(self):
        candidates = self.get_word_dictionary_for_length(self.word_length)

        # Filter out words that have already been used in this session
        unused_candidates = [w for w in candidates if w not in self.used_solutions]
        if not unused_candidates:
            # If all candidates used, fall back to full candidate list
            unused_candidates = list(candidates)

        # Hash Unix epoch time and session solution history to seed PRNG
        epoch_now = time.time()
        time_ns = time.time_ns()
        seed_raw = f"{epoch_now}:{time_ns}:{','.join(self.used_solutions)}:{random.randint(0, 1000000)}".encode("utf-8")
        seed_hash = hashlib.sha256(seed_raw).hexdigest()
        seed_int = int(seed_hash, 16)

        rng = random.Random(seed_int)
        chosen = rng.choice(unused_candidates).upper()
        self.used_solutions.append(chosen)
        return chosen

    def reset_game(self):
        self.secret_word = self.select_secret_word()
        self.attempts = []
        self.current_guess_slots = [""] * self.word_length
        self.selected_slot = None
        self.manual_insertion_done = False
        self.game_over = False
        self.game_won = False
        self.key_status = {}
        self.msg_banner.config(text="")

        self.rebuild_grid()
        self.rebuild_keyboard()

    def rebuild_grid(self):
        for widget in self.grid_container.winfo_children():
            widget.destroy()

        self.grid_labels = []
        for r in range(self.max_attempts):
            row_labels = []
            row_frame = tk.Frame(self.grid_container, bg="#121213")
            row_frame.pack(pady=2)
            for c in range(self.word_length):
                lbl = tk.Label(
                    row_frame,
                    text="",
                    font=("Helvetica", 18, "bold"),
                    width=2,
                    height=1,
                    fg=COLOR_TEXT,
                    bg=COLOR_DEFAULT,
                    bd=2,
                    relief=tk.SOLID,
                    highlightbackground=COLOR_BORDER,
                    highlightthickness=1,
                    cursor="hand2",
                )
                lbl.pack(side=tk.LEFT, padx=2)
                lbl.bind("<Button-1>", lambda e, row=r, slot=c: self.on_slot_click(row, slot))
                row_labels.append(lbl)
            self.grid_labels.append(row_labels)

    def on_slot_click(self, row, slot):
        if self.game_over or row != len(self.attempts):
            return

        if self.selected_slot == slot:
            self.selected_slot = None
        else:
            self.selected_slot = slot

        self.update_current_row_display()

    def rebuild_keyboard(self):
        for widget in self.keyboard_frame.winfo_children():
            widget.destroy()

        self.key_buttons = {}
        rows = [
            ["Q", "W", "E", "R", "T", "Y", "U", "I", "O", "P"],
            ["A", "S", "D", "F", "G", "H", "J", "K", "L"],
            ["ENTER", "Z", "X", "C", "V", "B", "N", "M", "BACKSPACE"]
        ]

        for row in rows:
            r_frame = tk.Frame(self.keyboard_frame, bg="#121213")
            r_frame.pack(pady=2)
            for key in row:
                disp_text = "⌫" if key == "BACKSPACE" else key
                btn = tk.Button(
                    r_frame,
                    text=disp_text,
                    font=("Helvetica", 10, "bold"),
                    fg="white",
                    bg="#818384",
                    activebackground="#a0a0a0",
                    activeforeground="white",
                    relief=tk.RAISED,
                    bd=1,
                    padx=6 if len(key) > 1 else 10,
                    pady=6,
                    command=lambda k=key: self.process_input(k),
                )
                btn.pack(side=tk.LEFT, padx=2)
                self.key_buttons[key] = btn

    def handle_keypress(self, event):
        if self.game_over:
            return

        if event.keysym == "Return":
            self.process_input("ENTER")
        elif event.keysym == "BackSpace":
            self.process_input("BACKSPACE")
        elif event.char and event.char.isalpha():
            char = event.char.upper()
            if len(char) == 1 and "A" <= char <= "Z":
                self.process_input(char)

    def process_input(self, key):
        if self.game_over:
            return

        if key == "ENTER":
            self.submit_guess()
        elif key == "BACKSPACE":
            self.msg_banner.config(text="")
            if self.manual_insertion_done:
                self.current_guess_slots = [""] * self.word_length
                self.manual_insertion_done = False
                self.selected_slot = None
            elif self.selected_slot is not None:
                self.current_guess_slots[self.selected_slot] = ""
                self.selected_slot = None
            else:
                for c in range(self.word_length - 1, -1, -1):
                    if self.current_guess_slots[c] != "":
                        self.current_guess_slots[c] = ""
                        break
            self.update_current_row_display()
        else:  # A-Z Letter input
            self.msg_banner.config(text="")
            if self.manual_insertion_done and self.selected_slot is None:
                # User starts typing after manual insertion -> overwrite attempt
                self.current_guess_slots = [""] * self.word_length
                self.manual_insertion_done = False
                self.current_guess_slots[0] = key
            elif self.selected_slot is not None:
                self.current_guess_slots[self.selected_slot] = key
                self.selected_slot = None
                self.manual_insertion_done = True
            else:
                # Standard append mode: find first empty slot
                for c in range(self.word_length):
                    if self.current_guess_slots[c] == "":
                        self.current_guess_slots[c] = key
                        break
            self.update_current_row_display()

    def update_current_row_display(self):
        row_idx = len(self.attempts)
        if row_idx >= self.max_attempts:
            return

        for c in range(self.word_length):
            lbl = self.grid_labels[row_idx][c]
            letter = self.current_guess_slots[c]
            lbl.config(text=letter, fg=COLOR_TEXT)

            if c == self.selected_slot:
                lbl.config(highlightbackground=COLOR_SELECTED, highlightthickness=2)
            else:
                lbl.config(highlightbackground=COLOR_BORDER, highlightthickness=1)

    def evaluate_guess(self, guess, secret):
        """
        Evaluate guess against secret word.
        Returns list of colors corresponding to each tile.
        """
        res = [COLOR_ABSENT] * self.word_length
        secret_chars = list(secret)
        guess_chars = list(guess)

        # First pass: green (correct position)
        for i in range(self.word_length):
            if guess_chars[i] == secret_chars[i]:
                res[i] = COLOR_CORRECT
                secret_chars[i] = None
                guess_chars[i] = None

        # Second pass: yellow (present in secret word)
        for i in range(self.word_length):
            if guess_chars[i] is not None and guess_chars[i] in secret_chars:
                res[i] = COLOR_PRESENT
                secret_chars[secret_chars.index(guess_chars[i])] = None

        return res

    def submit_guess(self):
        if not all(len(s) == 1 for s in self.current_guess_slots):
            return

        guess = "".join(self.current_guess_slots)

        # Check if guess is present in the internal word dictionary
        valid_words = self.get_word_dictionary_for_length(self.word_length)
        if guess not in valid_words:
            msg = f"'{guess}' is not in the internal word list! Please enter a valid English word."
            self.msg_banner.config(text=msg, fg="#e74c3c")
            if self.show_dialogs:
                messagebox.showwarning("Not a Valid Word", msg)
            return

        self.msg_banner.config(text="")
        row_idx = len(self.attempts)
        self.attempts.append(guess)

        colors = self.evaluate_guess(guess, self.secret_word)

        # Update Grid Tiles for current row
        for c in range(self.word_length):
            lbl = self.grid_labels[row_idx][c]
            letter = guess[c]

            # If secret_word has strictly more occurrences of this letter than the guess, set text color to blue
            secret_count = self.secret_word.count(letter)
            guess_count = guess.count(letter)
            text_color = COLOR_TEXT_MORE_INSTANCES if secret_count > guess_count else COLOR_TEXT

            lbl.config(bg=colors[c], fg=text_color, highlightbackground=COLOR_BORDER, highlightthickness=1)

            # Update key statuses
            current_status = self.key_status.get(letter, COLOR_DEFAULT)
            # Precedence: Correct > Present > Absent
            if colors[c] == COLOR_CORRECT:
                self.key_status[letter] = COLOR_CORRECT
            elif colors[c] == COLOR_PRESENT and current_status != COLOR_CORRECT:
                self.key_status[letter] = COLOR_PRESENT
            elif colors[c] == COLOR_ABSENT and current_status not in (COLOR_CORRECT, COLOR_PRESENT):
                self.key_status[letter] = COLOR_ABSENT

        self.update_keyboard_colors()

        if guess == self.secret_word:
            self.game_won = True
            self.game_over = True
            self.show_game_result(True)
        elif len(self.attempts) >= self.max_attempts:
            self.game_over = True
            self.show_game_result(False)
        else:
            self.current_guess_slots = [""] * self.word_length
            self.selected_slot = None
            self.manual_insertion_done = False

    def update_keyboard_colors(self):
        for letter, color in self.key_status.items():
            if letter in self.key_buttons:
                self.key_buttons[letter].config(bg=color)

    def show_game_result(self, won):
        row_idx = min(len(self.attempts), self.max_attempts) - 1
        if won:
            msg = f"Splendid! You guessed '{self.secret_word}' in {len(self.attempts)} attempt(s)."
        else:
            msg = f"Game Over! The word was '{self.secret_word}'."

        # Show message over grid container bottom or popup
        res_label = tk.Label(
            self,
            text=msg,
            font=("Helvetica", 12, "bold"),
            fg="#2ecc71" if won else "#e74c3c",
            bg="#121213",
            pady=5,
        )
        res_label.pack(side=tk.BOTTOM, pady=5)

    def return_to_menu(self):
        self.unbind_events()
        self.destroy()
        if self.return_to_menu_callback:
            self.return_to_menu_callback()


if __name__ == "__main__":
    root = tk.Tk()
    root.title("Wordle")
    root.geometry("500x650")
    game = WordleGame(root)
    root.mainloop()
