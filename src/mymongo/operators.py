"""Mongo operators enum mapping."""

from enum import Enum


class Operator(str, Enum):
    """MongoDB operators."""

    # https://www.mongodb.com/docs/manual/reference/operator/update/
    SET = "$set"

    # https://www.mongodb.com/docs/manual/reference/operator/query/
    ALL = "$all"
