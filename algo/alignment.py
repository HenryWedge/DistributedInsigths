from copy import deepcopy

SKIP = ">"
LOG_MOVE_COST = 1
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
        self.log_moves.append(f"{SKIP}({activity})")
        self.model_moves.append(str(activity))
        self.cost += LOG_MOVE_COST

    def model_move(self, activity, steps=1, original=None):
        self.log_moves.append(str(activity))
        self.model_moves.append(f"{SKIP}({str(activity)})")
        #self.model_moves.append(str(activity))
        self.cost += steps*MDL_MOVE_COST

    def concatenate(self, alignment: 'Alignment'):
        new_alignment = Alignment()
        new_alignment.model_moves.extend(deepcopy(self.model_moves))
        new_alignment.model_moves.extend(deepcopy(alignment.model_moves))
        new_alignment.log_moves.extend(deepcopy(self.log_moves))
        new_alignment.log_moves.extend(deepcopy(alignment.log_moves))
        new_alignment.cost = alignment.cost
        new_alignment.cost += self.cost
        return deepcopy(new_alignment)

    def skip_first(self):
        alignment = Alignment()
        alignment.model_moves = self.model_moves[1:]
        alignment.log_moves = self.log_moves[1:]
        alignment.cost = self.cost
        return alignment

    def __str__(self):
        return f"<log:{self.log_moves},mdl:{self.model_moves},cst:{self.cost}>"

    def __lt__(self, other):
        return False