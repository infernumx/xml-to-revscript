class DispatchTable(dict):
    def dispatch(self, key: str, values: tuple()):
        f = self.get(key)

        if not f:
            raise NotImplementedError(f'{key} has not been implemented.')

        argc = f.__code__.co_argcount

        return f(*values[:argc])


def dict_int_values(d: dict) -> dict:
    """Simple converter to turn all numeric dict values into integers"""
    ret = {}

    for key, val in d.items():
        try:
            ret[key] = int(val)
        except ValueError:
            ret[key] = val

    return ret


def lua_table(d: dict, indent: int=0) -> str:
    table_tab = '\t' * indent
    tab = '\t' * (indent + 1)
    ret = f'{table_tab}{{\n'

    if isinstance(d, dict):
        i = 0

        for k, v in d.items():
            i += 1
            comma = ',' if i != len(d.keys()) else ''
            if isinstance(v, list):
                ret += f'{tab}{k} = {{\n'
                for j, el in enumerate(v):
                    com = ',' if j != len(v) - 1 else ''
                    ret += f'{lua_table(el, indent=3)}{com}\n'
                ret += f'{tab}}}\n'
            else:
                value = (repr(v).lower()
                        if isinstance(v, bool)
                        else repr(v))
                ret += f'{tab}{k} = {value}{comma}\n'
    elif isinstance(d, list):
        for i, v in enumerate(d):
            comma = ',' if i != len(d) else ''
            ret += f'{lua_table(v, indent+1)}{comma}\n'

    return f'{ret}{table_tab}}}'
