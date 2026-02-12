
import math
from js import document, setTimeout
from pyodide.ffi import create_proxy
from pyscript import when

class TicTacToe:
    def __init__(self):
        self.board = [None] * 9
        self.current_player = "X"
        self.scores = {"X": 0, "O": 0, "Draws": 0}
        self.is_pve = True
        self.game_over = False
        self.winning_line = None
        self.setup_listeners()
        
    def setup_listeners(self):
        # Programmatic binding for squares
        for i in range(9):
            btn = document.getElementById(f"sq-{i}")
            # We use a closure to capture the index
            def create_click_handler(idx):
                return lambda e: self.handle_click(idx)
            btn.addEventListener("click", create_proxy(create_click_handler(i)))

        # Binding for action buttons
        document.getElementById("btn-reset-game").addEventListener("click", create_proxy(lambda e: self.reset()))
        document.getElementById("btn-play-again").addEventListener("click", create_proxy(lambda e: self.reset()))
        document.getElementById("btn-mode").addEventListener("click", create_proxy(lambda e: self.toggle_mode()))
        document.getElementById("btn-reset-scores").addEventListener("click", create_proxy(lambda e: self.reset_scores()))

    def check_winner(self, board):
        wins = [
            (0, 1, 2), (3, 4, 5), (6, 7, 8),
            (0, 3, 6), (1, 4, 7), (2, 5, 8),
            (0, 4, 8), (2, 4, 6)
        ]
        for a, b, c in wins:
            if board[a] and board[a] == board[b] == board[c]:
                return board[a], [a, b, c]
        if None not in board:
            return "Draw", None
        return None, None

    def minimax(self, board, depth, is_maximizing):
        winner, _ = self.check_winner(board)
        if winner == "O": return 10 - depth
        if winner == "X": return depth - 10
        if winner == "Draw": return 0
        
        if is_maximizing:
            best_score = -math.inf
            for i in range(9):
                if board[i] is None:
                    board[i] = "O"
                    score = self.minimax(board, depth + 1, False)
                    board[i] = None
                    best_score = max(score, best_score)
            return best_score
        else:
            best_score = math.inf
            for i in range(9):
                if board[i] is None:
                    board[i] = "X"
                    score = self.minimax(board, depth + 1, True)
                    board[i] = None
                    best_score = min(score, best_score)
            return best_score

    def get_ai_move(self):
        best_score = -math.inf
        move = -1
        for i in range(9):
            if self.board[i] is None:
                self.board[i] = "O"
                score = self.minimax(self.board, 0, False)
                self.board[i] = None
                if score > best_score:
                    best_score = score
                    move = i
        return move

    def handle_click(self, index):
        if self.game_over or self.board[index] is not None:
            return
            
        # Prevent AI turn interaction during player's turn if AI is active
        if self.is_pve and self.current_player == "O":
            return

        self.make_move(index)
        
        if not self.game_over and self.is_pve and self.current_player == "O":
            def ai_turn():
                move = self.get_ai_move()
                if move != -1:
                    self.make_move(move)
            
            setTimeout(create_proxy(ai_turn), 500)

    def make_move(self, index):
        if self.board[index] is not None:
            return

        self.board[index] = self.current_player
        winner, line = self.check_winner(self.board)
        
        self.update_ui_square(index)
        
        if winner:
            self.game_over = True
            self.winning_line = line
            if winner == "Draw":
                self.scores["Draws"] += 1
            else:
                self.scores[winner] += 1
            self.show_winner(winner)
        else:
            self.current_player = "O" if self.current_player == "X" else "X"
            self.update_status()

    def update_ui_square(self, index):
        square = document.getElementById(f"sq-{index}")
        val = self.board[index]
        square.innerHTML = val
        if val == "X":
            square.classList.add("neon-glow-x")
            square.classList.remove("neon-glow-o")
        else:
            square.classList.add("neon-glow-o")
            square.classList.remove("neon-glow-x")
        square.disabled = True

    def update_status(self):
        badge = document.getElementById("status-badge")
        if self.current_player == "X":
            badge.innerHTML = "X'S TURN"
            badge.style.borderColor = "#3b82f6"
            badge.style.boxShadow = "0 0 15px rgba(59, 130, 246, 0.3)"
            badge.style.backgroundColor = "rgba(59, 130, 246, 0.1)"
            badge.classList.remove("text-rose-400")
            badge.classList.add("text-blue-400")
        else:
            badge.innerHTML = "O'S TURN"
            badge.style.borderColor = "#f43f5e"
            badge.style.boxShadow = "0 0 15px rgba(244, 63, 94, 0.3)"
            badge.style.backgroundColor = "rgba(244, 63, 94, 0.1)"
            badge.classList.remove("text-blue-400")
            badge.classList.add("text-rose-400")

    def show_winner(self, winner):
        overlay = document.getElementById("winner-overlay")
        text = document.getElementById("winner-text")
        
        if winner == "Draw":
            text.innerHTML = "DRAW"
            text.className = "text-5xl md:text-7xl font-orbitron font-bold mb-4 text-slate-400"
        else:
            text.innerHTML = f"{winner} WINS"
            glow_class = "neon-glow-x" if winner == "X" else "neon-glow-o"
            text.className = f"text-5xl md:text-7xl font-orbitron font-bold mb-4 {glow_class}"
            
            # Highlight winning squares
            if self.winning_line:
                border_class = "neon-border-blue" if winner == "X" else "neon-border-rose"
                for i in self.winning_line:
                    document.getElementById(f"sq-{i}").classList.add(border_class)

        overlay.classList.remove("hidden")
        self.update_leaderboard()

    def update_leaderboard(self):
        document.getElementById("score-x").innerHTML = str(self.scores["X"])
        document.getElementById("score-o").innerHTML = str(self.scores["O"])
        document.getElementById("score-draws").innerHTML = str(self.scores["Draws"])

    def toggle_mode(self):
        self.is_pve = not self.is_pve
        btn_text = document.getElementById("mode-text")
        btn_text.innerHTML = "Vs Python AI" if self.is_pve else "Local PvP"
        btn_text.className = "font-semibold " + ("text-purple-400" if self.is_pve else "text-blue-400")
        self.reset()

    def reset_scores(self):
        self.scores = {"X": 0, "O": 0, "Draws": 0}
        self.update_leaderboard()
        self.reset()

    def reset(self):
        self.board = [None] * 9
        self.current_player = "X"
        self.game_over = False
        self.winning_line = None
        
        document.getElementById("winner-overlay").classList.add("hidden")
        for i in range(9):
            square = document.getElementById(f"sq-{i}")
            square.innerHTML = ""
            square.disabled = False
            # Clean up all state classes
            square.className = "square w-full h-24 md:h-32 flex items-center justify-center text-4xl md:text-6xl font-orbitron rounded-lg border-2 border-slate-800 bg-slate-900/50 hover:bg-slate-800/80"
        
        self.update_status()

# Initialize Game and store in global scope
game = TicTacToe()
