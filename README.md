# STAC Catalog for Trends.Earth

This project implements a SpatioTemporal Asset Catalog (STAC) structure to organize and document Trends.Earth JSON outputs. The catalog is built using the `pystac` Python library and adheres to the STAC specification standards. It provides a sustainable and standardized way to manage and access datasets such as NDVI, land degradation, and other Trends.Earth outputs.

This STAC catalog provides a foundation for organizing and documenting Trends.Earth outputs in a standardized and sustainable manner. For more information about STAC, visit the STAC specification website.

## Requirements

- Python 3.7+
- `pystac` library

Install the required library using pip:

```bash
pip install -r requirements.txt

```

## Usage
Clone the repository or download the project files.
Run the Python script to generate the STAC catalog:

```bash
python src/main.py
```
The catalog will be generated in the catalog/ directory.

Use the below command to validate the catalog using the stac validator tool:

```bash

stac-validator catalog/catalog.json

```


## Customization
More collections and items can be added by modifying the `create_country_collection` and `create_country_item` functions in the script.
The asset paths will also need to be updated in order to include additional files or datasets.

## License
This project is licensed under the MIT License. See the LICENSE file for details.
