import pystac
from pystac import Catalog, CatalogType, Collection, Item, Asset, Link
from pystac.extensions.eo import EOExtension
from datetime import datetime
import os

# Root catalog
def create_root_catalog():
    catalog = Catalog(
        id="trends-earth-catalog",
        description="A STAC catalog for organizing Trends.Earth JSON outputs.",
        title="Trends.Earth STAC Catalog"
    )
    return catalog

def create_country_collection(country_name):
    collection = Collection(
        id=f"{country_name}-collection",
        description=f"STAC Collection for {country_name} datasets",
        extent=pystac.Extent(
            spatial=pystac.SpatialExtent([[-180, -90, 180, 90]]),
            temporal=pystac.TemporalExtent([[datetime(2015, 1, 1), datetime.now()]])
        ),
        title=f"{country_name} Datasets"
    )
    return collection

def create_country_item(country_name, item_id, item_description, assets):
    item = Item(
        id=item_id,
        geometry=None,
        bbox=None, 
        datetime=datetime.now(),
        properties={}
    )
    for asset_key, asset_path in assets.items():
        item.add_asset(asset_key, Asset(href=asset_path))
    return item

def scan_data_folder(data_folder):
    countries = {}
    for root, dirs, files in os.walk(data_folder):
        print("Scanning folder {}, {}".format(root, dirs))
        if root == data_folder:
            countries = dirs
            break

    for country in countries:
        country_path = os.path.join(data_folder, country)
        datasets = {"drought": {}, "sdg-15-3-1": {}}
        for root, dirs, files in os.walk(country_path):
            for file in files:
                if "drought" in file:
                    asset_key = file.replace('.', '_')
                    datasets["drought"][asset_key] = os.path.relpath(os.path.join(root, file), start=data_folder)
                elif "sdg-15-3-1" in file:
                    asset_key = file.replace('.', '_')
                    datasets["sdg-15-3-1"][asset_key] = os.path.relpath(os.path.join(root, file), start=data_folder)
        yield country, datasets

def main():
    # Define the data folder path
    data_folder = "src/data"

    print(f"Creating STAC Trends Earth catalog")

    # Create the root catalog
    catalog = create_root_catalog()

    for country, datasets in scan_data_folder(data_folder):
        print(f"{country}: {len(datasets)}")
        country_collection = create_country_collection(country)

        if datasets["drought"]:
            drought_item = create_country_item(
                country,
                f"{country}_drought",
                f"STAC Item for {country} Drought Dataset",
                datasets["drought"]
            )
            country_collection.add_item(drought_item)

        if datasets["sdg-15-3-1"]:
            sdg_item = create_country_item(
                country,
                f"{country}_sdg_15_3_1",
                f"STAC Item for {country} SDG 15.3.1 Dataset",
                datasets["sdg-15-3-1"]
            )
            country_collection.add_item(sdg_item)

        catalog.add_child(country_collection)

    catalog.normalize_and_save(
        root_href="catalog",
        catalog_type=CatalogType.SELF_CONTAINED
    )

if __name__ == "__main__":
    main()