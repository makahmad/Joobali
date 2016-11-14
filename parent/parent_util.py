from models import Parent


def add_parent(parent_input):
    """Add a new parent object"""
    parent = Parent()
    existing_parent = get_parents_by_email(parent_input["email"])
    if existing_parent is None:
        parent.email = parent_input["email"]
        parent.put()
        return parent
    else:
        return existing_parent


def get_parents_by_email(email):
    qry = Parent.query(Parent.email == email)
    for parent in qry.fetch():
        return parent
