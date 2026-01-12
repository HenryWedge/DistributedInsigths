SKIP = ">"

class Alignment:
    def __init__(self):
        self.model_moves = []
        self.log_moves = []

    def sync_move(self, activity):
        self.model_moves.append(activity)
        self.log_moves.append(activity)

    def log_move(self, activity):
        self.model_moves.append(activity)
        self.log_moves.append(SKIP)

    def model_move(self, activity):
        self.model_moves.append(SKIP)
        self.log_moves.append(activity)

    def __str__(self):
        return f"{self.model_moves}\n{self.log_moves}"