from typing import Union

# --- Abstract Tool Definition (as per design) ---
class Tool:
    """
    Abstract base class for Tools. 
    The design defines 'description' and a 'use' method.
    We add 'name' to the class structure to facilitate the registry.
    """
    name: str
    description: str
    alias: str

    def use(self, args: str) -> Union[str, bool]:
        """
        Abstract method to execute the tool.
        Returns the output string or False on failure.
        """
        raise NotImplementedError("Tools must implement the use method.")