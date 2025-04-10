import json
import logging
import pystac
from pystac import Catalog, CatalogType, Collection, Item, Asset, Link
from datetime import datetime
import os

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def create_root_catalog():
    """Create the root STAC Catalog."""
    catalog = Catalog(
        id="trends-earth-catalog",
        description="Searchable spatiotemporal metadata describing Earth science "
                    "datasets hosted by the Trends.Earth platform.",
        title="Trends.Earth STAC API",
    )

    catalog.extra_fields.update({
        "conformsTo": [
            "https://api.stacspec.org/v1.0.0/item-search",
            "https://api.stacspec.org/v1.0.0-rc.2/item-search#filter",
            "http://www.opengis.net/spec/cql2/1.0/conf/basic-cql2",
            "http://www.opengis.net/spec/cql2/1.0/conf/cql2-text",
            "https://api.stacspec.org/v1.0.0/collections",
            "https://api.stacspec.org/v1.0.0/core",
            "http://www.opengis.net/spec/ogcapi-features-1/1.0/conf/oas30",
            "https://api.stacspec.org/v1.0.0/ogcapi-features",
            "https://api.stacspec.org/v1.0.0/item-search#fields",
            "https://api.stacspec.org/v1.0.0/item-search#query",
            "https://api.stacspec.org/v1.0.0/item-search#sort",
            "http://www.opengis.net/spec/ogcapi-features-3/1.0/conf/filter",
            "http://www.opengis.net/spec/ogcapi-features-1/1.0/conf/core",
            "http://www.opengis.net/spec/cql2/1.0/conf/cql2-json",
            "http://www.opengis.net/spec/ogcapi-features-1/1.0/conf/geojson"
        ]
    })

    return catalog


def create_country_collection(country_name):
    """Create a STAC Collection for a country."""
    collection = Collection(
        id=f"{country_name}-collection",
        description=f"STAC Collection for {country_name} datasets",
        extent=pystac.Extent(
            spatial=pystac.SpatialExtent([[-180, -90, 180, 90]]),
            temporal=pystac.TemporalExtent([[datetime(2015, 1, 1), datetime.now()]])
        ),
        title=f"{country_name} Datasets",
        license="proprietary",
        keywords=["Land Degradation", "Drought", "SDG 15.3.1", country_name]
    )

    collection.assets = {
        "thumbnail": Asset(
            href="https://docs.trends.earth/en/latest/_static/trends_earth_logo_square_32x32.ico",
            media_type="image/ico",
            roles=["thumbnail"],
            title=f"{country_name} Dataset Thumbnail"
        ),
    }

    collection.extra_fields.update({
        "trends:short_description": f"Land degradation and drought datasets for {country_name}",
        "trends:region": "global"
    })

    return collection


def create_country_item(
        country_name,
        item_id,
        item_description,
        assets,
        properties=None
):
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

    values = (
        summary_data.get("results", {})
        .get("data", {})
        .get("report", {})
        .get("land_condition", {})
        .get("baseline", {})
        .get("land_cover", {})
        .get("land_cover_areas_by_year", {})
        .get("values", {})
    )

    # Collect year-wise stats
    land_cover_by_year = []
    for year, classes in values.items():
        total_land_area = sum(classes.values())
        water_bodies = classes.get("Water body", 0)
        land_cover_by_year.append({
            "year": int(year),
            "total_land_area_km2": round(total_land_area, 2),
            "water_bodies_km2": round(water_bodies, 2)
        })

    properties = {
        "id": summary_data.get("id"),
        "status": summary_data.get("status"),
        "start_date": summary_data.get("start_date"),
        "end_date": summary_data.get("end_date"),
        "progress": summary_data.get("progress"),
        "task_name": summary_data.get("task_name"),
        "script_version": summary_data.get("script", {}).get("version"),
        "area_of_interest": summary_data.get("local_context", {}).get("area_of_interest_name"),
        "sdg_summary": summary_data.get("land_condition", {}).get("baseline", {}).get("sdg", {}).get("summary", {}),
        "land_cover_by_year": land_cover_by_year
    }
    return properties


def scan_data_folder(data_folder: str):
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
        drought_summary_file_path = os.path.join(
            country_path, "drought-vulnerability-summary_0.json")

        sdg_summary_file_path = None
        for file in os.listdir(country_path):
            if file.startswith("sdg-15-3-1-summary_") and file.endswith(".json"):
                sdg_summary_file_path = os.path.join(country_path, file)
                break

        drought_summary_data = read_summary_json(drought_summary_file_path)
        sdg_summary_data = read_summary_json(sdg_summary_file_path) if sdg_summary_file_path else {}

        drought_properties = extract_properties_from_drought_summary(drought_summary_data)
        sdg_properties = extract_properties_from_sdg_summary(sdg_summary_data)
        for root, dirs, files in os.walk(country_path):
            for file in files:
                print(f'file {file}')
                if "drought" in file and file != "drought-vulnerability-summary_0.json":
                    asset_key = file.replace('.', '_')
                    datasets["drought"][asset_key] = os.path.relpath(
                        os.path.join(root, file), start=data_folder)
                elif "sdg-15-3-1" in file:
                    asset_key = file.replace('.', '_')
                    datasets["sdg-15-3-1"][asset_key] = os.path.relpath(
                        os.path.join(root, file), start=data_folder)
        yield country, datasets, drought_properties, sdg_properties


def main():
    data_folder = "src/data"

    logger.info("Creating STAC Trends Earth catalog")

    # Create the root catalog
    catalog = create_root_catalog()

    for country, datasets, drought_properties, sdg_properties in scan_data_folder(data_folder):
        logger.info(f"{country}: {len(datasets)}")
        country_collection = create_country_collection(country)

        print(sdg_properties)

        if datasets["drought"]:
            drought_item = create_country_item(
                country,
                f"{country}_drought",
                f"STAC Item for {country} Drought Dataset",
                datasets["drought"],
                properties=drought_properties
            )
            country_collection.add_item(drought_item)

        if datasets["sdg-15-3-1"]:
            sdg_item = create_country_item(
                country,
                f"{country}_sdg_15_3_1",
                f"STAC Item for {country} SDG 15.3.1 Dataset",
                datasets["sdg-15-3-1"],
                properties=sdg_properties
            )
            print(sdg_item)
            country_collection.add_item(sdg_item)

        catalog.add_child(country_collection)

    catalog.normalize_and_save(
        root_href="catalog",
        catalog_type=CatalogType.SELF_CONTAINED
    )


if __name__ == "__main__":
    main()
