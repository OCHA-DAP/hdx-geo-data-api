# ruff: noqa: E501
app_description = """The HDX Geo Data API, built on top of FastAPI and GDAL.

Provides bindings from GDAL commands to API endpoints.

GDAL: `gdal vector convert --input=example.shp --output=example.geojson`

API: `/api/vector/convert?input=example.shp&output=example.geojson`

---

[GDAL documentation](https://gdal.org/en/stable/programs/index.html)

[API documentation](https://un-ocha-centre-for-humanitarian.gitbook.io/hdx-docs/build-with-hdx/build-with-hdx)

---
"""

descriptions = {
    "active_geometry": "Set the active geometry field from its name. When it is specified, only the specified geometry field will be subject to the processing. Other geometry fields will be not modified. If this option is not specified, all geometry fields will be subject to the processing. This option can be combined together with `active_layer`.",
    "active_layer": "Set the active layer. When it is specified, only the layer specified by its name will be subject to the processing. Other layers will be not modified. If this option is not specified, all layers will be subject to the processing.",
    "bbox": 'Bounds to which to filter the dataset. They are assumed to be in the CRS of the input dataset. The X and Y axis are the "GIS friendly ones", that is X is longitude or easting, and Y is latitude or northing. Note that filtering does not clip geometries to the bounding box. Provided as `xmin,ymin,xmax,ymax`.',
    "config": "Configuration option. May be repeated. Use values from [GDAL configuration options](https://gdal.org/en/stable/user/configoptions.html#list-of-configuration-options-and-where-they-are-documented). Provided as `KEY=VALUE`.",
    "creation_option": "Many formats have one or more optional dataset creation options that can be used to control particulars about the file created. For instance, the GeoPackage driver supports creation options to control the version. May be repeated. The dataset creation options available vary by format driver, and some simple formats have no creation options at all. See [vector drivers](https://gdal.org/en/stable/drivers/vector/index.html) format specific documentation for the creation options of each format. Note that dataset creation options are different from layer creation options. Provided as `KEY=VALUE`.",
    "dialect": "By default the native SQL of an RDBMS is used. If a datasource does not support SQL natively, the default is to use the [OGRSQL dialect](https://gdal.org/en/stable/user/ogr_sql_dialect.html) (`OGRSQL`), which can also be specified with any data source. The [SQL SQLite dialect](https://gdal.org/en/stable/user/sql_sqlite_dialect.html) can be chosen with the `SQLITE` and `INDIRECT_SQLITE` dialect values, and this can be used with any data source. Overriding the default dialect may be beneficial because the capabilities of the SQL dialects vary.",
    "features": "List all features by default, unless limited with `limit`. Beware of RAM consumption on large layers. This option is mutually exclusive with the `summary` option.",
    "input_format": "Format to be attempted to open the input file. It is generally not necessary to specify it, but it can be used to skip automatic driver detection, when it fails to select the appropriate driver. This option can be repeated several times to specify several candidate drivers. Note that it does not force those drivers to open the dataset. In particular, some drivers have requirements on file extensions. May be repeated. Use values from [vector driver](https://gdal.org/en/stable/drivers/vector/index.html) short name.",
    "input_layer": "Name of one or more layers to process. May be repeated. If no layer names are passed, then all layers will be selected.",
    "input": "Input vector dataset (required). Uses HDX [resource_id](https://un-ocha-centre-for-humanitarian.gitbook.io/hdx-docs/build-with-hdx/build-with-hdx/overview/hdx-core-concepts#data-resources). Provided as UUID v4 `xxxxxxxx-xxxx-4xxx-xxxx-xxxxxxxxxxxx`.",
    "layer_creation_option": "Many formats have one or more optional layer creation options that can be used to control particulars about the layer created. For instance, the GeoPackage driver supports layer creation options to control the feature identifier or geometry column name, setting the identifier or description, etc. May be repeated. The layer creation options available vary by format driver, and some simple formats have no layer creation options at all. See [vector drivers](https://gdal.org/en/stable/drivers/vector/index.html) format specific documentation for the layer creation options of each format. Note that layer creation options are different from dataset creation options. Provided as `KEY=VALUE`.",
    "limit": "Limit the number of features reported per layer. When set, this implies `features`.",
    "open_option": "Open option for the input vector dataset. Format specific, may be repeated. Available values differ for each [vector driver](https://gdal.org/en/stable/drivers/vector/index.html). Provided as `KEY=VALUE`.",
    "output_format": "Which output vector format to use. Use a value from [vector driver](https://gdal.org/en/stable/drivers/vector/index.html) short name that supports creation. If not specified, infers format from output extension.",
    "output_layer": "Output layer name. Can only be used to rename a layer, if there is a single input layer.",
    "output": "Output vector dataset (required). The output format will be inferred by the file extension (example.geojson).",
    "preserve_boundary": "Flag indicating whether to preserve (avoid simplifying) external boundaries. This can be useful when simplifying a portion of a larger dataset. If not specified, `false`.",
    "skip_errors": "Whether failures to write feature(s) should be ignored. If not specified, `false`.",
    "sql": "Execute the indicated SQL statement and return the result. Editing capabilities depend on the dialect selected with `dialect`. Mutually exclusive with `input_layer` and `where`.",
    "summary": "Provide a summary with the list of layers and the geometry type of each layer. This option is mutually exclusive with the `features` option.",
    "tolerance": "Tolerance used for determining whether vertices should be removed (required). Specified in georeferenced units of the source layer.",
    "where": "Attribute query in a restricted form of the queries used in the [SQL WHERE statement](https://gdal.org/en/stable/user/ogr_sql_dialect.html#where).",
}
