class AlignmentElement:
    def __init__(self, model, log):
        self.model = model
        self.log = log

    def __str__(self):
        return f"Model: {self.model} | Log: {self.log}"

    def __lt__(self, other):
        return False

    def __hash__(self):
        return 0

    def __eq__(self, other):
        return self.model == other.model and self.log == other.log