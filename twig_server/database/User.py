from neomodel import (StructuredNode, UniqueIdProperty, StringProperty, EmailProperty);

class User(StructuredNode):
    uid = UniqueIdProperty()
    username = StringProperty(unique_index = True)
    email = EmailProperty(unique_index = True)
