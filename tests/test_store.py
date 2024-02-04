"""Test the store."""
from mongomock import Collection
from pydantic import BaseModel, EmailStr
from querytyper import MongoFilterMeta, MongoQuery

from mymongo.document import Document
from mymongo.store import Store


def test_integration(mock_collection: Collection) -> None:
    """Test the store."""

    class User(BaseModel):
        """User model."""

        name: str
        age: int
        email: EmailStr

    class UserInDb(User, Document):
        """User database model."""

    class UserFilter(UserInDb, metaclass=MongoFilterMeta):
        """User query filter."""

    store = Store[User, UserInDb](collection=mock_collection)
    first_id = store.create(User(name="John", age=11, email="john@example.com")).id
    second_id = store.create(User(name="John", age=13, email="j@example.com")).id
    store.create(User(name="Al", age=12, email="al@example.com"))
    query = MongoQuery((UserFilter.name == "John") & (UserFilter.age >= 10))
    store.delete(first_id)
    found = store.find(query)
    assert len(found) == 1
    assert found[0].id == second_id
