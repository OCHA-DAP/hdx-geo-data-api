from typing import Annotated
from uuid import UUID

from fastapi import Query
from pydantic import BaseModel

description = {
    "active_layer": "Set active layer (if not specified, all)",
    "bbox": "Bounding box as xmin,ymin,xmax,ymax",
    "config": "Configuration option [may be repeated]",
    "creation_option": "Creation option [may be repeated]",
    "input_format": "Input formats [may be repeated], use short name from https://gdal.org/en/stable/drivers/vector/index.html",
    "input_layer": "Input layer name(s) [may be repeated]",
    "layer_creation_option": "Layer creation option [may be repeated]",
    "open_option": "Open option [may be repeated]",
    "output_format": "Output format, use short name from https://gdal.org/en/stable/drivers/vector/index.html",
    "output_layer": "Output layer name",
    "where": "Attribute query in a restricted form of the queries used in the SQL WHERE statement",  # noqa: E501
}


class InputModel(BaseModel):
    input: Annotated[UUID, Query()]


class OutputModel(InputModel):
    output: Annotated[str, Query()]


class VectorBaseModel(OutputModel):
    config: Annotated[
        list[str] | None,
        Query(description=description["config"]),
    ] = None
    creation_option: Annotated[
        list[str] | None,
        Query(description=description["creation_option"]),
    ] = None
    input_format: Annotated[
        list[str] | None,
        Query(description=description["input_format"]),
    ] = None
    layer_creation_option: Annotated[
        list[str] | None,
        Query(description=description["layer_creation_option"]),
    ] = None
    open_option: Annotated[
        list[str] | None,
        Query(description=description["open_option"]),
    ] = None
    output_format: Annotated[
        str | None,
        Query(description=description["output_format"]),
    ] = None
    output_layer: Annotated[
        str | None,
        Query(description=description["output_layer"]),
    ] = None


class ConvertModel(VectorBaseModel):
    input_layer: Annotated[
        list[str] | None,
        Query(description=description["input_layer"]),
    ] = None


class FilterModel(VectorBaseModel):
    active_layer: Annotated[
        str | None,
        Query(description=description["active_layer"]),
    ] = None
    bbox: Annotated[
        str | None,
        Query(description=description["bbox"]),
    ] = None
    where: Annotated[
        str | None,
        Query(description=description["where"]),
    ] = None


VectorModel = ConvertModel | FilterModel
