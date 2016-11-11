from models import Parent


def add_parent(parent_input):
    """Add a new parent object"""
    parent = Parent()
    existing_parent = get_parents_by_email(parent["email"])
    if get_parents_by_email(parent["email"]) != None:
        parent.email = parent["email"]
        parent.put()
        return parent
    else:
        return existing_parent


def get_parents_by_email(email):
    qry = Parent.query(Parent.email == email, keys_only=True)
    for parent in qry.fetch():
        return parent
