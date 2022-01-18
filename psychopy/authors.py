from datetime import datetime
import inspect
from pathlib import Path

# Array of contributors
contributors = []


# Method to create an author - works like a standard class constructor, but can return an extant Author object rather than always making a new one
def Author(surname, forename, middlenames=None, email=None, github=None, orcid=None, other=None):
    # Create _Author object with same inputs as this function was called with
    obj = _Author(surname, forename, middlenames=middlenames, email=email, github=github, orcid=orcid, other=other)
    # If that author is already listed in contributors, return the same object they're referenced as
    for auth in contributors:
        if auth == obj:
            return auth
    # If not listed in contributors, add it and return it
    contributors.append(obj)
    return obj


class _Author:
    """
    An easily referenceable author.

    surname : str
        Author's surname, e.g. Peirce for Jon Peirce
    forename : str
        Author's forename, e.g. Jon for Jon Peirce
    middlenames : list
        List of author's middle names, if they have any. e.g. ['Ethan'] for Todd Ethan Parsons
    email : str
        Author's email address, if they have one. e.g. jon@opensciencetools.org for Jon Peirce
    github : str
        Author's GitHub username, if they have one. e.g. peircej for Jon Peirce
    orcid : str or int
        Author's ORCiD, if they have one. e.g. 0000000261928414 for Todd Parsons
    other : dict
        Any other links or details the author may want included, such as a website link or Twitter username.
    """
    def __init__(self, surname, forename, middlenames=None, email=None, github=None, orcid=None, other=None):
        assert isinstance(surname, str) and isinstance(forename, str), (
            "When crediting an author, surname and forename must be strings."
        )
        # Store first and last names
        self.surname = surname.lower()
        self.forename = forename.lower()
        # Store middle names, coerced to list format
        if isinstance(middlenames, list):
            self.middlenames = middlenames
        elif isinstance(middlenames, tuple):
            self.middlenames = list(middlenames)
        elif isinstance(middlenames, str):
            self.middlenames = [middlenames]
        else:
            self.middlenames = []
        # Store email if given
        self.email = email
        # Store ORCiD if given
        if orcid is None:
            self.orcid = None
        else:
            self.orcid = str(orcid).replace("-", "")
        # Store GitHub if given
        self.github = github
        # Store any other given
        self.other = other or {}

        # Create array to store accreditations
        self.refs = []

    def __eq__(self, other):
        # If the other object isn't an Author, it isn't the same
        if not isinstance(other, self.__class__):
            return False
        # If both have an orcid id, use that
        if self.orcid is not None and other.orcid is not None:
            print(self.orcid, other.orcid)
            return self.orcid == other.orcid
        # If both have a github username, use that
        if self.github is not None and other.github is not None:
            return self.github == other.github
        # If both have an email, use that
        if self.email is not None and other.email is not None:
            return self.email == other.email
        # Otherwise, compare first and last names
        same = self.forename == other.forename and self.surname == other.surname
        # If middle names are present in both objects, make sure they match
        if self.middlenames and other.middlenames:
            for mname in self.middlenames:
                same = same and other.middlenames.count(mname) == 1

        return same

    def __repr__(self):
        return (
            f"<Author: {self}>"
        )

    def __str__(self):
        # Get middle names as initials
        if self.middlenames:
            initials = "".join([mname[0].capitalize() + ". " for mname in self.middlenames])
        else:
            initials = ""
        # Get github username in brackets with an @
        if self.github:
            github = f" (@{self.github})"
        else:
            github = ""
        # Construct and return string
        return (
            f"{self.forename.capitalize()} {initials}{self.surname.capitalize()}{github}: "
            f"{len(self.classes)} class{'es' if len(self.classes) != 1 else ''}, "
            f"{len(self.functions)} function{'s' if len(self.functions) != 1 else ''}."
        )

    def credit(self, contrib):
        """
        Credit this author with working on a particular class, function or module.
        """
        # Add the contribution to their references
        if contrib not in self.refs:
            self.refs.append(contrib)
        # Return own handle for one-line crediting
        return self

    @property
    def classes(self):
        """
        List of classes credited to this author in modules which have been imported
        """
        return [ref for ref in self.refs if inspect.isclass(ref)]

    @property
    def functions(self):
        """
        List of functions credited to this author in modules which have been imported
        """
        return [ref for ref in self.refs if inspect.isfunction(ref) or inspect.ismethod(ref)]

# Synonymise docs for Author and _Author
Author.__doc__ = _Author.__doc__


# Add some authors with full details here so they can be referenced by just name elsewhere
peircej = Author(
    "Peirce", "Jon",
    email="jon@opensciencetools.org",
    github="peircej",
    other={
        "website": "https://www.nottingham.ac.uk/psychology/people/jonathan.peirce",
        "twitter": "@peircej",
    }
)
TEParsons = Author(
    "Parsons", "Todd", middlenames=["Ethan"],
    email="todd@opensciencetools.org",
    github="TEParsons",
    orcid="0000000261928414",
    other={
        "website": "toddparsons.co.uk",
        "twitter": "@ToddEParsons",
    }
)
TEParsons.credit(_Author)

