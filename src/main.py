import json
import logging
import pystac
from pystac import Catalog, CatalogType, Collection, Item, Asset
from datetime import datetime
import os

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

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

def create_country_item(country_name, item_id, item_description, assets, properties=None):
    item = Item(
        id=item_id,
        geometry=None,
        bbox=None,
        datetime=datetime.now(),
        properties=properties if properties else {}
    )
    for asset_key, asset_path in assets.items():
        item.add_asset(asset_key, Asset(href=asset_path))
    return item

def read_summary_json(file_path):
    """Read and parse the summary JSON file."""
    if not os.path.exists(file_path):
        logger.warning(f"Summary file {file_path} does not exist.")
        return None

    with open(file_path, "r") as f:
        try:
            return json.load(f)
        except json.JSONDecodeError as e:
            logger.error(f"Error parsing JSON file {file_path}: {e}")
            return None

def extract_properties_from_drought_summary(summary_data):
    """Extract relevant properties from the drought summary JSON data."""
    if not summary_data:
        return {}

    properties = {
        "id": summary_data.get("id"),
        "status": summary_data.get("status"),
        "start_date": summary_data.get("start_date"),
        "end_date": summary_data.get("end_date"),
        "progress": summary_data.get("progress"),
        "task_name": summary_data.get("task_name"),
        "script_version": summary_data.get("script", {}).get("version"),
        "area_of_interest": summary_data.get("local_context", {}).get("area_of_interest_name"),
        "drought_summary": summary_data.get("results", {}).get("data", {}).get("report", {}).get("drought")
    }
    return properties

def extract_properties_from_sdg_summary(summary_data):
    """Extract relevant properties from the SDG summary JSON data."""
    if not summary_data:
        return {}

    properties = {
        "id": summary_data.get("id"),
        "status": summary_data.get("status"),
        "start_date": summary_data.get("start_date"),
        "end_date": summary_data.get("end_date"),
        "progress": summary_data.get("progress"),
        "task_name": summary_data.get("task_name"),
        "script_version": summary_data.get("script", {}).get("version"),
        "area_of_interest": summary_data.get("local_context", {}).get("area_of_interest_name"),
        "sdg_summary": summary_data.get("land_condition", {}).get("baseline", {}).get("sdg", {}).get("summary")
    }
    return properties

def scan_data_folder(data_folder):
    if not os.path.exists(data_folder):
        logger.error(f"Data folder {data_folder} does not exist.")
        return

    countries = {}
    for root, dirs, files in os.walk(data_folder):
        logger.info(f"Scanning folder {root}, {dirs}")
        if root == data_folder:
            countries = dirs
            break

    for country in countries:
        country_path = os.path.join(data_folder, country)
        datasets = {"drought": {}, "sdg-15-3-1": {}}
        drought_summary_file_path = os.path.join(country_path, "drought_summary.json")
        sdg_summary_file_path = os.path.join(country_path, "sdg-15-3-1_summary.json")

        # Read the summary files
        drought_summary_data = read_summary_json(drought_summary_file_path)
        sdg_summary_data = read_summary_json(sdg_summary_file_path)

        drought_properties = extract_properties_from_drought_summary(drought_summary_data)
        sdg_properties = extract_properties_from_sdg_summary(sdg_summary_data)

        for root, dirs, files in os.walk(country_path):
            for file in files:
                if "drought" in file and file != "drought_summary.json":
                    asset_key = file.replace('.', '_')
                    datasets["drought"][asset_key] = os.path.relpath(os.path.join(root, file), start=data_folder)
                elif "sdg-15-3-1" in file and file != "sdg-15-3-1_summary.json":
                    asset_key = file.replace('.', '_')
                    datasets["sdg-15-3-1"][asset_key] = os.path.relpath(os.path.join(root, file), start=data_folder)
        yield country, datasets, drought_properties, sdg_properties

def main():
    # Define the data folder path
    data_folder = "src/data"

    logger.info("Creating STAC Trends Earth catalog")

    # Create the root catalog
    catalog = create_root_catalog()

    for country, datasets, drought_properties, sdg_properties in scan_data_folder(data_folder):
        logger.info(f"{country}: {len(datasets)}")
        country_collection = create_country_collection(country)

        if datasets["drought"]:
            drought_item = create_country_item(
                country,
                f"{country}_drought",
                f"STAC Item for {country} Drought Dataset",
                datasets["drought"],
                properties=drought_properties  # Add properties from the drought summary file
            )
            country_collection.add_item(drought_item)

        if datasets["sdg-15-3-1"]:
            sdg_item = create_country_item(
                country,
                f"{country}_sdg_15_3_1",
                f"STAC Item for {country} SDG 15.3.1 Dataset",
                datasets["sdg-15-3-1"],
                properties=sdg_properties  # Add properties from the SDG summary file
            )
            country_collection.add_item(sdg_item)

        catalog.add_child(country_collection)

    catalog.normalize_and_save(
        root_href="catalog",
        catalog_type=CatalogType.SELF_CONTAINED
    )

if __name__ == "__main__":
    main()