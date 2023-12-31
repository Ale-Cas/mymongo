"""Test the Document class."""
from collections.abc import Generator

import pytest
from mongomock import Collection, Database, MongoClient

from mymongo.document import Document, DocumentType


@pytest.fixture()
def mockdb() -> Generator[Database, None, None]:
    """Mock database client fixture."""
    client: MongoClient[DocumentType] = MongoClient()
    _db_name = "test"
    yield client.get_database(name=_db_name)
    client.drop_database(_db_name)


@pytest.fixture()
def collection(mockdb: Database) -> Collection:
    """Mock database client fixture."""
    return mockdb.get_collection(name="test")


@pytest.fixture()
def document(collection: Collection) -> Document:
    """Return a Document instance."""
    Document.set_collection(collection=collection)
    return Document()


@pytest.fixture()
def created_document(document: Document) -> Document:
    """Test the create method of the Document class."""
    return document.create()


class TestSubDocument(Document):
    """TestDocument class."""

    test_field: str = "test"


@pytest.fixture()
def subdocument(collection: Collection) -> TestSubDocument:
    """Return a TestSubDocument instance."""
    return TestSubDocument(collection=collection)
