import inspect


class Author:
    _refs = {}

    def __init__(self, name, ref=None):
        # Store name
        self.name = name
        if ref is not None:
            # Store thing the author is attributed to, if given
            if self.name not in Author._refs:
                Author._refs[self.name] = []
            Author._refs[self.name].append(ref)

    def __repr__(self):
        return (f"<"
                f"Author: {self.name}, {len(self.all)} contribution(s): "
                f"{len(self.classes)} class(es), {len(self.functions)} function(s)"
                f">")

    @property
    def all(self):
        """
        List of all contributions credited to this author in modules which have been imported
        """
        if self.name in Author._refs:
            return Author._refs[self.name]
        else:
            return []

    @property
    def classes(self):
        """
        List of classes credited to this author in modules which have been imported
        """
        if self.name in Author._refs:
            return [ref for ref in Author._refs[self.name] if inspect.isclass(ref)]
        else:
            return []

    @property
    def functions(self):
        """
        List of functions credited to this author in modules which have been imported
        """
        if self.name in Author._refs:
            return [ref for ref in Author._refs[self.name] if inspect.isfunction(ref) or inspect.ismethod(ref)]
        else:
            return []


def getAllAuthors():
    """
    List all authors credited in modules which have been imported
    """
    # Get all authors currently referenced
    auths = [Author(name) for name in Author._refs]
    # Sort by number of contribs
    auths.sort(key=lambda obj: len(obj.all), reverse=True)
    return auths
