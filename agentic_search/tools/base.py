class BaseTool:
    """
    Base class for tools. Extend for custom tools.
    """
    name: str
    description: str

    def run(self, *args, **kwargs):
        raise NotImplementedError("Tool.run must be implemented by subclasses.")
