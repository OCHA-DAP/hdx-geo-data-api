# ruff: noqa: UP040
from typing import Annotated, TypeAlias

from fastapi import Query
from pydantic import BaseModel

from .docs import descriptions as d

Bool = bool | None
Int = int | None
Many = list[str] | None
One = str | None

ActiveGeometry: TypeAlias = Annotated[One, Query(description=d["active_geometry"])]
ActiveLayer: TypeAlias = Annotated[One, Query(description=d["active_layer"])]
Bbox: TypeAlias = Annotated[One, Query(description=d["bbox"])]
Config: TypeAlias = Annotated[Many, Query(description=d["config"])]
CreationOption: TypeAlias = Annotated[Many, Query(description=d["creation_option"])]
Dialect: TypeAlias = Annotated[One, Query(description=d["dialect"])]
Features: TypeAlias = Annotated[Bool, Query(description=d["features"])]
Input: TypeAlias = Annotated[str, Query(description=d["input"])]
InputFormat: TypeAlias = Annotated[Many, Query(description=d["input_format"])]
InputLayer: TypeAlias = Annotated[Many, Query(description=d["input_layer"])]
LayerCreationOption: TypeAlias = Annotated[
    Many,
    Query(description=d["layer_creation_option"]),
]
Limit: TypeAlias = Annotated[Int, Query(description=d["limit"])]
OpenOption: TypeAlias = Annotated[Many, Query(description=d["open_option"])]
Output: TypeAlias = Annotated[str, Query(description=d["output"])]
OutputFormat: TypeAlias = Annotated[One, Query(description=d["output_format"])]
OutputLayer: TypeAlias = Annotated[One, Query(description=d["output_layer"])]
OutputOpenOption: TypeAlias = Annotated[
    Many,
    Query(description=d["output_open_option"]),
]
PreserveBoundary: TypeAlias = Annotated[
    Bool,
    Query(description=d["preserve_boundary"]),
]
SkipErrors: TypeAlias = Annotated[Bool, Query(description=d["skip_errors"])]
Sql: TypeAlias = Annotated[One, Query(description=d["sql"])]
Summary: TypeAlias = Annotated[Bool, Query(description=d["summary"])]
Tolerance: TypeAlias = Annotated[float, Query(description=d["tolerance"])]
Where: TypeAlias = Annotated[One, Query(description=d["where"])]


class InfoModel(BaseModel):
    # required options
    input: Input
    # common options
    config: Config = None
    # options
    input_layer: InputLayer = None
    features: Features = None
    summary: Summary = None
    limit: Limit = None
    sql: Sql = None
    where: Where = None
    dialect: Dialect = None
    # advanced options
    open_option: OpenOption = None
    input_format: InputFormat = None


class ConvertModel(BaseModel):
    # required options
    input: Input
    output: Output
    # common options
    config: Config = None
    # options
    input_layer: InputLayer = None
    output_format: OutputFormat = None
    creation_option: CreationOption = None
    layer_creation_option: LayerCreationOption = None
    output_layer: OutputLayer = None
    # advanced options
    input_format: InputFormat = None
    open_option: OpenOption = None
    output_open_option: OutputOpenOption = None


class FilterModel(BaseModel):
    # required options
    input: Input
    output: Output
    # common options
    config: Config = None
    # options
    input_layer: InputLayer = None
    output_format: OutputFormat = None
    creation_option: CreationOption = None
    layer_creation_option: LayerCreationOption = None
    output_layer: OutputLayer = None
    skip_errors: SkipErrors = None
    active_layer: ActiveLayer = None
    bbox: Bbox = None
    where: Where = None
    # advanced options
    input_format: InputFormat = None
    open_option: OpenOption = None
    output_open_option: OutputOpenOption = None


class SimplifyModel(BaseModel):
    # required options
    input: Input
    output: Output
    tolerance: Tolerance
    # common options
    config: Config = None
    # options
    input_layer: InputLayer = None
    output_format: OutputFormat = None
    creation_option: CreationOption = None
    layer_creation_option: LayerCreationOption = None
    output_layer: OutputLayer = None
    skip_errors: SkipErrors = None
    active_layer: ActiveLayer = None
    preserve_boundary: PreserveBoundary = None
    # advanced options
    input_format: InputFormat = None
    open_option: OpenOption = None
    output_open_option: OutputOpenOption = None


VectorFileModel = ConvertModel | FilterModel | SimplifyModel
