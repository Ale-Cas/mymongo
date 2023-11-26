"""Document model."""
from collections.abc import Iterable, Mapping
from datetime import datetime
from typing import Any

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
COLLECTION = "collection"


class DocumentNotFoundError(Exception):
    """Document not found error."""


class Document(BaseModel):
    """A class representing a document in MongoDB."""

    model_config = ConfigDict(arbitrary_types_allowed=True)

    collection: Collection[DocumentType] | MockCollection = Field(
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
        result = self.collection.insert_one(
            self.to_document_type(exclude={COLLECTION}),
        )
        self.id = result.inserted_id
        return self

    def read(
        self,
        id: bson.ObjectId,  # noqa: A002
        strict: bool = True,
    ) -> Self:
        """
        Read the document to the specified collection.

        collection : Collection[DocumentType]
            The MongoDB collection to update the document in.
        """
        document_found = self.collection.find_one({ID: id})
        if document_found is None:
            raise DocumentNotFoundError(f"Document with id={id} not found.")
        return self.model_validate({**document_found, COLLECTION: self.collection}, strict=strict)

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
        return self.collection.update_one(
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
        return self.collection.delete_one({ID: id})


Documents = Iterable[Document]
