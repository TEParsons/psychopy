import ast
from pathlib import Path
from .authors import authors
from ._base import Credit, Author

tags = []


def findAuthors(node, context, lastParent):
    global tags

    if not hasattr(node, "body"):
        return

    if lastParent == "module":
        # Detect types of module
        for thisType, path in {
            "demo": "psychopy/demos",
            "component": "psychopy/experiment/components",
            "test": "psychopy/tests",
        }.items():
            try:
                context.relative_to(path)
            except ValueError:
                pass
            else:
                lastParent = thisType

    for subnode in node.body:
        if isinstance(subnode, ast.Assign):
            # If node is an assignment, check for the __author__ tag
            for target in subnode.targets:
                if isinstance(target, ast.Name):
                    if target.id == "__author__":
                        # If this is an __author__, add an entry for each author
                        names = subnode.value.value
                        names = names.replace(",", "&").replace(";", "&")
                        for name in names.split("&"):
                            tags.append({
                                "name": name.strip(),
                                "type": lastParent,
                                "context": str(context).replace(".py", "")
                            })
        elif isinstance(subnode, (ast.Module, ast.ClassDef, ast.FunctionDef)):
            # Update last known parent acording to node type
            if isinstance(subnode, ast.Module):
                lastParent = "module"
            elif isinstance(subnode, ast.ClassDef):
                lastParent = "class"
            elif isinstance(subnode, ast.FunctionDef):
                lastParent = "function"
            # Append node name to context and recur
            findAuthors(
                subnode,
                context=context / subnode.name,
                lastParent=lastParent
            )


# Get library root
libroot = Path(__file__).parent.parent

# Recursively iterate through Python files
for file in libroot.rglob("*.py"):
    # Read file
    with file.open("rb") as f:
        script = f.read()
    # Mark module if current file is an init file
    if file.stem == "__init__":
        module = file.parent.relative_to(libroot.parent)
    else:
        module = file.relative_to(libroot.parent)
    # Parse file
    tree = ast.parse(script)
    # Recursively populate `tags` with list of __author__ tags
    findAuthors(tree, context=module, lastParent="module")


for tag in tags:
    authorMatch = [auth == tag['name'] for auth in authors]
    if any(authorMatch):
        # If author recognised, use it
        author = authors[authorMatch.index(True)]
    else:
        # If unrecognised name, add a new author object
        names = tag['name'].split(" ")
        author = Author(forename=names[0], surname=names[-1])
        authors.append(author)
    # Credit author
    cred = Credit(context=tag['context'], type=tag['type'])
    author.credit(cred)
