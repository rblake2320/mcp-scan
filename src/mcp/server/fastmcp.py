class FastMCP:
    def __init__(self, name: str):
        self.name = name

    def tool(self):
        def decorator(fn):
            return fn
        return decorator

    def run(self):
        pass
