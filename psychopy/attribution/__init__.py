import ast
from pathlib import Path
from .authors import authors
from ._base import Credit

tags = []


def findAuthors(node, context, lastParent):
    global tags

    if not hasattr(node, "body"):
        return

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
        module = file.parent.relative_to(libroot)
    else:
        module = file.relative_to(libroot)
    # Parse file
    tree = ast.parse(script)
    # Recursively populate `tags` with list of __author__ tags
    findAuthors(tree, context=module, lastParent="module")

for author in authors:
    for tag in tags:
        if author == tag["name"]:
            cred = Credit(tag["name"], context=tag['context'], type=tag['type'])
            author.credit(cred)
