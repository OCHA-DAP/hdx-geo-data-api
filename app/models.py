from typing import Annotated

from fastapi import Query
from pydantic import BaseModel

from .docs import descriptions as d

One = str | None
Many = list[str] | None


class InputModel(BaseModel):
    input: Annotated[str, Query(description=d["input"])]


class OutputModel(InputModel):
    output: Annotated[str, Query(description=d["output"])]


class VectorBaseModel(OutputModel):
    config: Annotated[Many, Query(description=d["config"])] = None
    creation_option: Annotated[Many, Query(description=d["creation_option"])] = None
    input_format: Annotated[Many, Query(description=d["input_format"])] = None
    layer_creation_option: Annotated[
        Many,
        Query(description=d["layer_creation_option"]),
    ] = None
    open_option: Annotated[Many, Query(description=d["open_option"])] = None
    output_format: Annotated[One, Query(description=d["output_format"])] = None
    output_layer: Annotated[One, Query(description=d["output_layer"])] = None


class ConvertModel(VectorBaseModel):
    input_layer: Annotated[Many, Query(description=d["input_layer"])] = None


class FilterModel(VectorBaseModel):
    active_layer: Annotated[One, Query(description=d["active_layer"])] = None
    bbox: Annotated[One, Query(description=d["bbox"])] = None
    where: Annotated[One, Query(description=d["where"])] = None


class GeometryModel(VectorBaseModel):
    active_geometry: Annotated[One, Query(description=d["active_geometry"])] = None
    active_layer: Annotated[One, Query(description=d["active_layer"])] = None


class SimplifyModel(GeometryModel):
    tolerance: Annotated[str, Query(description=d["tolerance"])]


VectorModel = ConvertModel | FilterModel | SimplifyModel
