SKIP = ">"
LOG_MOVE_COST = 5
MDL_MOVE_COST = 1
SKIP_NODE_COST = 3

class Alignment:
    def __init__(self):
        self.model_moves = []
        self.log_moves = []
        self.cost: int = 0

    def is_empty(self):
        return len(self.model_moves) == 0 and len(self.log_moves) == 0

    def sync_move(self, activity):
        self.model_moves.append(str(activity))
        self.log_moves.append(str(activity))

    def log_move(self, activity):
        self.model_moves.append(str(activity))
        self.log_moves.append(SKIP)
        self.cost += LOG_MOVE_COST

    def model_move(self, activity, steps):
        self.model_moves.append(SKIP)
        self.model_moves.append(str(activity))
        self.log_moves.append(str(activity))
        self.cost += steps*MDL_MOVE_COST

    def __str__(self):
        return f"<log:{self.log_moves},mdl:{self.model_moves},cst:{self.cost}>"