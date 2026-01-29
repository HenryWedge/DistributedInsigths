from collections import deque


class Context[T]:
    def __init__(self, limit: int | None):
        self.context = deque([], maxlen=limit)

    def push(self, t: T):
        self.context.append(t)

    def get(self):
        return list(self.context)

    def get_last(self) -> T:
        return self.get()[-1]

if __name__ == '__main__':
    context = Context(2)
    context.push('a')
    context.push('b')
    context.push('c')
    context.push('d')
    context.push('e')
    context.push('f')
    context.push('g')
    print(context.get())