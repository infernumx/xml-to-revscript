class DispatchTable(dict):
    def dispatch(self, i, values):
        f = self.get(i)
        if not f:
            raise NotImplementedError(f'{i} has not been implemented.')
        argc = f.__code__.co_argcount
        return f(*values[:argc])
