import json
import random
import re
import tkinter as tk
from tkinter import messagebox, simpledialog, ttk
import urllib.parse
import urllib.request

# Offline fallback graph for offline testing and fast deterministic fallback
FALLBACK_GRAPH = {
    "Python (programming language)": ["Guido van Rossum", "Linux", "C (programming language)", "JavaScript", "FreeBSD"],
    "Guido van Rossum": ["Netherlands", "Python (programming language)", "Google", "Dropbox"],
    "Netherlands": ["Amsterdam", "Europe", "European Union", "Dutch language"],
    "Amsterdam": ["Netherlands", "Capital city", "North Holland", "Canal"],
    "Europe": ["Continent", "European Union", "Asia", "Earth"],
    "European Union": ["Europe", "Brussels", "Euro", "Treaty of Maastricht"],
    "C (programming language)": ["Dennis Ritchie", "Bell Labs", "Unix", "C++"],
    "Dennis Ritchie": ["C (programming language)", "Unix", "Turing Award", "Harvard University"],
    "Unix": ["Operating system", "Bell Labs", "Linux", "POSIX"],
    "Linux": ["Operating system", "Linus Torvalds", "Unix", "Free software"],
    "Linus Torvalds": ["Linux", "Git", "Finland", "Helsinki"],
    "Finland": ["Helsinki", "Europe", "Nordic countries", "Swedish language"],
    "Helsinki": ["Finland", "Capital city", "Baltic Sea"],
    "JavaScript": ["Brendan Eich", "Web browser", "HTML", "Netscape"],
    "HTML": ["World Wide Web", "SGML", "Tim Berners-Lee", "HTTP"],
    "Tim Berners-Lee": ["World Wide Web", "CERN", "HTML", "HTTP"],
    "World Wide Web": ["Internet", "Hypertext", "Tim Berners-Lee", "URI"],
    "Internet": ["Computer network", "IP address", "World Wide Web", "ARPANET"],
    "Earth": ["Planet", "Solar System", "Sun", "Moon"],
    "Solar System": ["Sun", "Planet", "Milky Way", "Gravitational bound system"],
    "Sun": ["Star", "Solar System", "Hydrogen", "Helium"],
    "Moon": ["Natural satellite", "Earth", "Apollo 11", "Gravity"]
}


def fetch_opening_links(title, use_network=True):
    """
    Fetches the opening text Wikipedia links for a given title.
    Falls back to offline graph if network fails or network is disabled.
    """
    if use_network:
        try:
            url = f"https://en.wikipedia.org/w/api.php?action=query&titles={urllib.parse.quote(title)}&prop=revisions&rvprop=content&format=json&redirects=1"
            req = urllib.request.Request(url, headers={"User-Agent": "SixDegreesOfWikipedia/1.0"})
            with urllib.request.urlopen(req, timeout=4) as resp:
                data = json.loads(resp.read().decode("utf-8"))
                pages = data.get("query", {}).get("pages", {})
                page = list(pages.values())[0]
                if "missing" not in page and "revisions" in page:
                    actual_title = page.get("title", title)
                    wikitext = page["revisions"][0]["*"]
                    intro = re.split(r"==|__TOC__", wikitext)[0]
                    raw_links = re.findall(r"\[\[([^\]\|#]+)(?:\|[^\]]+)?\]\]", intro)
                    filtered = []
                    ignore_namespaces = [
                        "Category", "File", "Image", "Help", "Special",
                        "Wikipedia", "Template", "Portal", "Draft", "User", "Talk"
                    ]
                    for l in raw_links:
                        l_str = l.strip()
                        if l_str and not any(l_str.startswith(ns + ":") for ns in ignore_namespaces):
                            l_norm = l_str[0].upper() + l_str[1:]
                            if l_norm not in filtered and l_norm != actual_title:
                                filtered.append(l_norm)
                    if filtered:
                        return actual_title, filtered
        except Exception:
            pass

    # Fallback graph lookup
    norm_title = title[0].upper() + title[1:] if title else title
    if norm_title in FALLBACK_GRAPH:
        return norm_title, list(FALLBACK_GRAPH[norm_title])

    # Case-insensitive search in fallback graph
    for key in FALLBACK_GRAPH:
        if key.lower() == title.lower():
            return key, list(FALLBACK_GRAPH[key])

    # Synthetic fallback for custom title
    synthetic_links = random.sample(list(FALLBACK_GRAPH.keys()), min(4, len(FALLBACK_GRAPH)))
    return norm_title, synthetic_links


class SixDegreesGame(tk.Frame):
    def __init__(self, parent, return_to_menu_callback=None, use_network=True, show_dialogs=True):
        super().__init__(parent, bg="#1a252f")
        self.parent = parent
        self.return_to_menu_callback = return_to_menu_callback
        self.use_network = use_network
        self.show_dialogs = show_dialogs

        # Configurable settings
        self.random_start = True
        self.chain_length = 6
        self.max_attempts = 6
        self.infinite_attempts = False

        # Game State
        self.start_page = ""
        self.target_page = ""
        self.chain = []
        self.attempts_used = 0
        self.current_links = []
        self.game_over = False
        self.game_won = False

        self.setup_ui()
        self.reset_game()

    def setup_ui(self):
        self.pack(fill=tk.BOTH, expand=True)

        # Header bar
        self.header_frame = tk.Frame(self, bg="#2c3e50")
        self.header_frame.pack(fill=tk.X, side=tk.TOP)

        title_label = tk.Label(
            self.header_frame,
            text="🌐 Six Degrees of Wikipedia",
            font=("Helvetica", 14, "bold"),
            fg="#ecf0f1",
            bg="#2c3e50",
            padx=10,
            pady=8,
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
            text="New Game",
            command=self.reset_game,
            bg="#3498db",
            fg="white",
            font=("Helvetica", 10, "bold"),
            relief=tk.FLAT,
            padx=8,
        )
        self.restart_btn.pack(side=tk.RIGHT, padx=5, pady=5)

        # Configuration Panel
        self.config_frame = tk.Frame(self, bg="#243342", padx=10, pady=8)
        self.config_frame.pack(fill=tk.X, padx=15, pady=10)

        # Random Start Toggle
        self.random_start_var = tk.BooleanVar(value=True)
        self.random_cb = tk.Checkbutton(
            self.config_frame,
            text="Random Start Page",
            variable=self.random_start_var,
            command=self.on_config_change,
            bg="#243342",
            fg="#ecf0f1",
            selectcolor="#1a252f",
            activebackground="#243342",
            activeforeground="#ecf0f1",
            font=("Helvetica", 9, "bold"),
        )
        self.random_cb.grid(row=0, column=0, sticky="w", padx=5)

        # Chain Length Option
        tk.Label(
            self.config_frame, text="Chain Length:", bg="#243342", fg="#ecf0f1", font=("Helvetica", 9, "bold")
        ).grid(row=0, column=1, sticky="e", padx=(15, 2))

        self.chain_length_var = tk.IntVar(value=6)
        self.chain_spin = tk.Spinbox(
            self.config_frame, from_=2, to=10, width=3, textvariable=self.chain_length_var, font=("Helvetica", 9)
        )
        self.chain_spin.grid(row=0, column=2, sticky="w", padx=2)

        # Max Attempts Option
        tk.Label(
            self.config_frame, text="Max Attempts:", bg="#243342", fg="#ecf0f1", font=("Helvetica", 9, "bold")
        ).grid(row=0, column=3, sticky="e", padx=(15, 2))

        self.max_attempts_var = tk.IntVar(value=6)
        self.attempts_spin = tk.Spinbox(
            self.config_frame, from_=1, to=20, width=3, textvariable=self.max_attempts_var, font=("Helvetica", 9)
        )
        self.attempts_spin.grid(row=0, column=4, sticky="w", padx=2)

        self.infinite_var = tk.BooleanVar(value=False)
        self.infinite_cb = tk.Checkbutton(
            self.config_frame,
            text="Unlimited",
            variable=self.infinite_var,
            bg="#243342",
            fg="#ecf0f1",
            selectcolor="#1a252f",
            activebackground="#243342",
            activeforeground="#ecf0f1",
            font=("Helvetica", 9),
        )
        self.infinite_cb.grid(row=0, column=5, sticky="w", padx=5)

        self.apply_cfg_btn = tk.Button(
            self.config_frame,
            text="Apply Settings",
            command=self.apply_settings_and_reset,
            bg="#2ecc71",
            fg="white",
            font=("Helvetica", 9, "bold"),
            relief=tk.FLAT,
            padx=6,
        )
        self.apply_cfg_btn.grid(row=0, column=6, padx=(15, 5))

        # Target Objective Banner
        self.objective_frame = tk.Frame(self, bg="#1a252f", pady=5)
        self.objective_frame.pack(fill=tk.X, padx=15)

        self.target_label = tk.Label(
            self.objective_frame,
            text="",
            font=("Helvetica", 11, "bold"),
            fg="#f1c40f",
            bg="#1a252f",
            wraplength=480,
            justify=tk.CENTER,
        )
        self.target_label.pack()

        # Chain Progress Display
        self.chain_frame = tk.LabelFrame(
            self, text="Current Chain", bg="#1a252f", fg="#bdc3c7", font=("Helvetica", 9, "bold"), padx=10, pady=5
        )
        self.chain_frame.pack(fill=tk.X, padx=15, pady=5)

        self.chain_label = tk.Label(
            self.chain_frame,
            text="",
            font=("Helvetica", 10),
            fg="#2ecc71",
            bg="#1a252f",
            wraplength=460,
            justify=tk.LEFT,
        )
        self.chain_label.pack(side=tk.LEFT, fill=tk.X, expand=True)

        self.undo_btn = tk.Button(
            self.chain_frame,
            text="↩ Undo Step",
            command=self.undo_step,
            bg="#e67e22",
            fg="white",
            font=("Helvetica", 9, "bold"),
            relief=tk.FLAT,
            padx=6,
        )
        self.undo_btn.pack(side=tk.RIGHT)

        # Links Selector Listbox with scrollbar
        self.links_frame = tk.LabelFrame(
            self, text="Links in Current Opening Text (Double click or Select & Click Add)", bg="#1a252f", fg="#bdc3c7", font=("Helvetica", 9, "bold"), padx=10, pady=5
        )
        self.links_frame.pack(fill=tk.BOTH, expand=True, padx=15, pady=5)

        self.scrollbar = tk.Scrollbar(self.links_frame)
        self.scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        self.links_listbox = tk.Listbox(
            self.links_frame,
            font=("Helvetica", 11),
            bg="#2c3e50",
            fg="#ecf0f1",
            selectbackground="#3498db",
            selectforeground="white",
            yscrollcommand=self.scrollbar.set,
            bd=0,
            highlightthickness=0,
        )
        self.links_listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        self.scrollbar.config(command=self.links_listbox.yview)

        self.links_listbox.bind("<Double-Button-1>", self.on_link_double_click)

        # Action bar under listbox
        self.action_frame = tk.Frame(self, bg="#1a252f", pady=5)
        self.action_frame.pack(fill=tk.X, padx=15, pady=(0, 10))

        self.add_link_btn = tk.Button(
            self.action_frame,
            text="Follow Selected Link",
            command=self.follow_selected_link,
            bg="#3498db",
            fg="white",
            font=("Helvetica", 10, "bold"),
            relief=tk.FLAT,
            padx=12,
            pady=4,
        )
        self.add_link_btn.pack(side=tk.LEFT)

        self.status_label = tk.Label(
            self.action_frame,
            text="",
            font=("Helvetica", 10, "italic"),
            fg="#bdc3c7",
            bg="#1a252f",
        )
        self.status_label.pack(side=tk.RIGHT)

    def on_config_change(self):
        pass

    def apply_settings_and_reset(self):
        try:
            self.chain_length = int(self.chain_length_var.get())
            self.max_attempts = int(self.max_attempts_var.get())
            self.infinite_attempts = self.infinite_var.get()
            self.random_start = self.random_start_var.get()
            self.reset_game()
        except ValueError:
            pass

    def generate_game_pair(self):
        if not self.random_start and self.show_dialogs:
            prompt_title = simpledialog.askstring("Start Page", "Enter a starting Wikipedia page title:", parent=self)
            if prompt_title and prompt_title.strip():
                start = prompt_title.strip()
            else:
                start = "Python (programming language)"
        elif not self.random_start:
            start = "Python (programming language)"
        else:
            seed_pages = list(FALLBACK_GRAPH.keys())
            start = random.choice(seed_pages)

        curr_title, curr_links = fetch_opening_links(start, use_network=self.use_network)
        if not curr_title:
            curr_title = start
            curr_links = list(FALLBACK_GRAPH.get("Python (programming language)", []))

        # Perform random walk up to chain_length steps to pick a target page
        visited_path = [curr_title]
        current = curr_title
        links = curr_links

        for _ in range(min(self.chain_length, 6)):
            if not links:
                break
            next_page = random.choice(links)
            visited_path.append(next_page)
            t_title, t_links = fetch_opening_links(next_page, use_network=self.use_network)
            if t_title and t_links:
                current = t_title
                links = t_links
            else:
                current = next_page
                links = list(FALLBACK_GRAPH.get(next_page, []))

        target = current if current != curr_title else (links[0] if links else "Earth")
        return curr_title, target

    def reset_game(self):
        self.game_over = False
        self.game_won = False
        self.attempts_used = 0

        self.start_page, self.target_page = self.generate_game_pair()
        self.chain = [self.start_page]

        self.update_game_state()

    def update_game_state(self):
        curr_page = self.chain[-1]
        actual_title, self.current_links = fetch_opening_links(curr_page, use_network=self.use_network)

        # Update labels
        attempts_str = "Unlimited" if self.infinite_attempts else f"{self.attempts_used}/{self.max_attempts}"
        self.target_label.config(
            text=f"Connect: '{self.start_page}' ➔ '{self.target_page}' (Max Chain: {self.chain_length})"
        )

        chain_str = " ➔ ".join(self.chain)
        self.chain_label.config(text=chain_str)

        self.status_label.config(text=f"Attempts Used: {attempts_str}")

        # Update Listbox
        self.links_listbox.delete(0, tk.END)
        for link in self.current_links:
            self.links_listbox.insert(tk.END, link)

        # Check Win / Loss condition
        if curr_page.lower() == self.target_page.lower():
            self.game_won = True
            self.game_over = True
            self.status_label.config(text="🎉 YOU WIN! Target Reached!", fg="#2ecc71")
            if self.show_dialogs:
                messagebox.showinfo("Victory!", f"Congratulations! You connected to '{self.target_page}' in {len(self.chain) - 1} steps!")
        elif not self.infinite_attempts and self.attempts_used >= self.max_attempts:
            self.game_over = True
            self.status_label.config(text="❌ Game Over! Max Attempts Reached.", fg="#e74c3c")

    def follow_selected_link(self):
        if self.game_over:
            return

        sel = self.links_listbox.curselection()
        if not sel:
            return

        chosen_link = self.links_listbox.get(sel[0])
        self.attempts_used += 1
        self.chain.append(chosen_link)
        self.update_game_state()

    def on_link_double_click(self, event):
        self.follow_selected_link()

    def undo_step(self):
        if self.game_over or len(self.chain) <= 1:
            return

        self.chain.pop()
        self.update_game_state()

    def return_to_menu(self):
        self.destroy()
        if self.return_to_menu_callback:
            self.return_to_menu_callback()


if __name__ == "__main__":
    root = tk.Tk()
    root.title("Six Degrees of Wikipedia")
    root.geometry("550x650")
    game = SixDegreesGame(root)
    root.mainloop()
