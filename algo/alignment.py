SKIP = ">"

class Alignment:
    def __init__(self):
        self.model_moves = []
        self.log_moves = []

    def sync_move(self, activity):
        self.model_moves.append(str(activity))
        self.log_moves.append(str(activity))

    def log_move(self, activity):
        self.model_moves.append(str(activity))
        self.log_moves.append(SKIP)

    def model_move(self, activity):
        self.model_moves.append(SKIP)
        self.model_moves.append(str(activity))
        self.log_moves.append(str(activity))

    def __str__(self):
        return f"{self.log_moves}\n{self.model_moves}"