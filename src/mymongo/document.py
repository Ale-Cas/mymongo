"""Document model."""
from collections.abc import Mapping
from datetime import datetime
from functools import lru_cache
from typing import Any, ClassVar, cast

import bson
from mongomock.collection import Collection as MockCollection
from pydantic import BaseModel, ConfigDict, Field
from pymongo.collection import Collection
from pymongo.results import DeleteResult, UpdateResult
from typing_extensions import Self

from mymongo.operators import Operator
from mymongo.utils import utcnow

DocumentType = Mapping[str, Any]


ID = "_id"
_Collection = Collection[DocumentType] | MockCollection


class DocumentNotFoundError(Exception):
    """Document not found error."""


class Document(BaseModel):
    """A class representing a document in MongoDB."""

    model_config = ConfigDict(arbitrary_types_allowed=True)

    collection: ClassVar[_Collection | None] = Field(
        default=None,
        description="The MongoDB collection the document is in.",
    )

    id: None | bson.ObjectId = Field(  # noqa: A003
        alias=ID,
        default=None,
        description="The document unique identifier in MongoDB.",
    )
    created_at: None | datetime = Field(
        default=None,
        description="The datetime when the document was created in MongoDB.",
    )
    updated_at: None | datetime = Field(
        default=None,
        description="The datetime when the document was updated in MongoDB last time.",
    )
    deleted_at: None | datetime = Field(
        default=None,
        description="The datetime when the document was deleted in MongoDB.",
    )

    def to_document_type(
        self,
        exclude: None | set[str] = None,
    ) -> DocumentType:
        """Dump to a general typed dict for pymongo and override."""
        return self.model_dump(by_alias=True, exclude=exclude, exclude_none=True)

    @classmethod
    def set_collection(
        cls,
        collection: _Collection,
    ) -> None:
        """Set the collection for the document class."""
        cls.collection = collection

    @classmethod
    @lru_cache(maxsize=1)
    def get_collection(cls) -> _Collection:
        """Check if the collection is set and return it."""
        if cls.collection is None:
            raise ValueError(f"You must set a collection for {cls.__name__}.")
        return cls.collection

    @classmethod
    def parse_from_db(
        cls,
        db_document: DocumentType,
    ) -> Self:
        """Parse the document from the database."""
        return cls.model_validate(db_document)

    def create(
        self,
    ) -> Self:
        """
        Create the document to the specified collection.

        collection : Collection[DocumentType]
            The MongoDB collection to update the document in.
        """
        if self.id is not None:
            raise ValueError(f"{self.__class__.__name__} has already an id={self.id}.")
        self.created_at = utcnow()
        result = self.get_collection().insert_one(
            self.to_document_type(),
        )
        self.id = result.inserted_id
        return self

    @classmethod
    def read(
        cls,
        id: bson.ObjectId,  # noqa: A002
    ) -> "MongoDocument":
        """
        Read the document from the specified collection.

        Parameters
        ----------
        id : bson.ObjectId
            The ID of the document to read.
        strict : bool, optional
            Whether to perform strict validation on the document, by default True.

        Returns
        -------
        Self
            The document parsed with data validation.

        Raises
        ------
        DocumentNotFoundError
            If the document with the specified ID is not found.
        """
        document_found = cls.get_collection().find_one({ID: id})
        if document_found is None:
            raise DocumentNotFoundError(f"Document with id={id} not found.")
        return cast(MongoDocument, cls.parse_from_db(document_found))

    def update(
        self,
        patch: DocumentType,
        strict: bool = True,
    ) -> UpdateResult:
        """
        Update the document in the specified collection.

        Parameters
        ----------
        collection : Collection[DocumentType]
            The MongoDB collection to update the document in.
        """
        # validate the merged model before updating
        self.model_validate({**patch, **self.to_document_type()}, strict=strict)
        return self.get_collection().update_one(
            filter={
                # if the patch has an ID use that
                # otherwise use the document's ID
                ID: patch.get(ID, None) or self.id,
            },
            update={Operator.SET: {**patch, "updated_at": utcnow()}},
        )

    def delete(
        self,
        id: bson.ObjectId,  # noqa: A002
    ) -> DeleteResult:
        """
        Delete the document from the specified collection.

        Args:
            collection: The MongoDB collection to delete the document from.
        """
        self.deleted_at = utcnow()
        return self.get_collection().delete_one({ID: id})

    @classmethod
    def find_all(cls) -> list[Self]:
        """Find all documents in the collection."""
        return [cls.parse_from_db(doc) for doc in cls.get_collection().find({})]


class MongoDocument(Document):
    """A class representing a document saved in MongoDB with required _id and created_at."""

    id: bson.ObjectId = Field(  # noqa: A003
        alias=ID,
        description="The document unique identifier in MongoDB.",
    )
    created_at: datetime = Field(
        description="The datetime when the document was created in MongoDB.",
    )
