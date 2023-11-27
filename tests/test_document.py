"""Test the Document class."""
import bson
import pytest
from pymongo.results import DeleteResult, UpdateResult

from mymongo.document import Document, DocumentNotFoundError
from tests.conftest import TestSubDocument


def test_to_document_type(document: Document) -> None:
    """Test the to_document_type method of the Document class."""
    result = document.to_document_type()
    assert isinstance(result, dict)


def test_get_collection_error() -> None:
    """Test the get_collection method of the Document class."""
    Document.collection = None
    with pytest.raises(ValueError, match="You must set a collection for Document."):
        Document.get_collection()


def test_create(document: Document) -> None:
    """Test the create method of the Document class."""
    result = document.create()
    assert isinstance(result, Document)
    assert result.id is not None
    assert result.id == document.id


def test_create_value_error(created_document: Document) -> None:
    """Test the create method of the Document class."""
    assert created_document.id is not None
    with pytest.raises(
        ValueError,
        match=f"{created_document.__class__.__name__} has already an id={created_document.id}.",
    ):
        created_document.create()


def test_read(created_document: Document) -> None:
    """Test the read method of the Document class."""
    assert created_document.id
    result = Document.read(created_document.id)
    assert result.id == created_document.id
    assert isinstance(result, Document)


def test_read_not_found_error(document: Document) -> None:
    """Test the read method of the Document class."""
    _id = bson.ObjectId()
    with pytest.raises(DocumentNotFoundError, match=f"Document with id={_id} not found."):
        document.read(_id)


def test_update(subdocument: TestSubDocument) -> None:
    """Test the update method of the Document class."""
    new_value = "new_value"
    subdocument = subdocument.create()
    result = subdocument.update({"test_field": new_value})
    assert isinstance(result, UpdateResult)
    updated_subdocument = subdocument.read(subdocument.id)
    assert updated_subdocument.id == subdocument.id
    assert updated_subdocument.test_field == new_value


def test_delete(created_document: Document) -> None:
    """Test the delete method of the Document class."""
    assert created_document.id
    result = created_document.delete(created_document.id)
    assert isinstance(result, DeleteResult)
    assert result.deleted_count == 1
    assert result.raw_result["ok"] == float(1)


def test_find_all(created_document: Document) -> None:
    """Test the find_all method of the Document class."""
    results = Document.find_all()
    assert isinstance(results, list)
    assert len(results) == 1
    result = results[0]
    assert isinstance(result, Document)
    assert created_document.id
    assert result.id == created_document.id
