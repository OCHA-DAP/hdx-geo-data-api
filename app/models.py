# ruff: noqa: UP040
from typing import Annotated, TypeAlias

from pydantic import BaseModel, Field

from .docs import descriptions as d

Bool = bool | None
Int = int | None
Many = list[str] | None
One = str | None

ActiveGeometry: TypeAlias = Annotated[One, Field(description=d["active_geometry"])]
ActiveLayer: TypeAlias = Annotated[One, Field(description=d["active_layer"])]
Bbox: TypeAlias = Annotated[One, Field(description=d["bbox"])]
Config: TypeAlias = Annotated[Many, Field(description=d["config"])]
CreationOption: TypeAlias = Annotated[Many, Field(description=d["creation_option"])]
Dialect: TypeAlias = Annotated[One, Field(description=d["dialect"])]
Features: TypeAlias = Annotated[Bool, Field(description=d["features"])]
Input: TypeAlias = Annotated[str, Field(description=d["input"])]
InputFormat: TypeAlias = Annotated[Many, Field(description=d["input_format"])]
InputLayer: TypeAlias = Annotated[Many, Field(description=d["input_layer"])]
LayerCreationOption: TypeAlias = Annotated[
    Many,
    Field(description=d["layer_creation_option"]),
]
Limit: TypeAlias = Annotated[Int, Field(description=d["limit"])]
OpenOption: TypeAlias = Annotated[Many, Field(description=d["open_option"])]
Output: TypeAlias = Annotated[str, Field(description=d["output"])]
OutputFormat: TypeAlias = Annotated[One, Field(description=d["output_format"])]
OutputLayer: TypeAlias = Annotated[One, Field(description=d["output_layer"])]
PreserveBoundary: TypeAlias = Annotated[Bool, Field(description=d["preserve_boundary"])]
SkipErrors: TypeAlias = Annotated[Bool, Field(description=d["skip_errors"])]
Sql: TypeAlias = Annotated[One, Field(description=d["sql"])]
Summary: TypeAlias = Annotated[Bool, Field(description=d["summary"])]
Tolerance: TypeAlias = Annotated[float, Field(description=d["tolerance"])]
Where: TypeAlias = Annotated[One, Field(description=d["where"])]


class Info(BaseModel):
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

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "input": "Foo",
                },
            ],
        },
    }


class Convert(BaseModel):
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


class Filter(BaseModel):
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


class Simplify(BaseModel):
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
    active_geometry: ActiveGeometry = None
    # advanced options
    input_format: InputFormat = None
    open_option: OpenOption = None


class SimplifyCoverage(BaseModel):
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


VectorFile = Convert | Filter | Simplify | SimplifyCoverage
