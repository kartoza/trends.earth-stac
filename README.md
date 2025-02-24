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
python create_stac_catalog.py
```
The catalog will be generated in the catalog/ directory.

Validate the catalog using the stac command-line tool:

```bash

stac-validator catalog/catalog.json

```


## Customization
Add more collections and items by modifying the `create_country_collection` and `create_country_item` functions in the script.

Update the asset paths to include additional files or datasets.

## Contributing
Contributions are welcome! If you have suggestions or improvements, please open an issue or submit a pull request.

## License
This project is licensed under the MIT License. See the LICENSE file for details.
