from dataclasses import is_dataclass, fields

def ast_to_dict(node):
    """
    Recursively converts AST dataclasses into JSON-serializable dictionaries.
    """

    if node is None:
        return None

    if isinstance(node, list):
        return [ast_to_dict(n) for n in node]

    if is_dataclass(node):
        result = {
            "type": node.__class__.__name__
        }

        for field in fields(node):
            result[field.name] = ast_to_dict(getattr(node, field.name))

        return result

    return node