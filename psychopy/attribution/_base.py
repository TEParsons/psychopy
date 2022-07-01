class Author:
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
    def __init__(self, surname, forename, middlenames=[], email="", github="", orcid="", other=None):
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
        self.orcid = str(orcid).replace("-", "")
        # Store GitHub if given
        self.github = str(github).replace("@", "")
        # Store any other given
        self.other = other or {}

        # Create array to store accreditations
        self.refs = []

    def __eq__(self, other):
        # Comparing to another Author...
        if isinstance(other, self.__class__):
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

        # Comparing to a string
        if isinstance(other, str):
            # Standardise and split
            other = other.lower().replace(".", "").replace(",", "")
            parts = other.split(" ")
            # If string is this Author's orcid, github or email, return True
            if self.orcid.lower() in parts:
                return True
            if self.github.lower() in parts:
                return True
            if self.email.lower() in parts:
                return True
            # Work out whether it's this Author's name
            if self.surname not in parts:
                return False
            if not (self.forename in parts or self.forename[0] in parts):
                return False
            middles = parts
            for excl in (self.forename, self.forename[0], self.surname):
                if excl in middles:
                    i = middles.index(excl)
                    middles.pop(i)
            if not len(middles):
                return True
            middleInitials = [name[0].lower for name in self.middlenames]
            same = True
            for part in middles:
                if (part not in self.middlenames) or (part not in middleInitials):
                    same = False
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
            f"{len(self.modules)} module{'s' if len(self.modules) != 1 else ''}, "
            f"{len(self.classes)} class{'es' if len(self.classes) != 1 else ''}, "
            f"{len(self.functions)} function{'s' if len(self.functions) != 1 else ''}."
        )

    @property
    def contributions(self):
        """
        List of all contributions by this author
        """
        return self.refs

    @property
    def modules(self):
        """
        List of modules credited to this author
        """
        return [ref for ref in self.refs if ref.type == "module"]

    @property
    def classes(self):
        """
        List of classes credited to this author
        """
        return [ref for ref in self.refs if ref.type == "class"]

    @property
    def functions(self):
        """
        List of functions credited to this author
        """
        return [ref for ref in self.refs if ref.type == "function"]

    def credit(self, contrib):
        """
        Credit this author with working on a particular class, function or module.
        """
        # Add the contribution to their references
        self.refs.append(contrib)


class Credit:
    def __init__(self, name, context, type):
        self.name = name
        self.context = context
        self.type = type

    def __repr__(self):
        return f"<{type(self).__name__}: {self.type}, {self.context} by {self.name}>"
