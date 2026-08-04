from pathlib import Path
import random

import pandas as pd
from faker import Faker


NUMBER_OF_ROWS = 100_000
RANDOM_SEED = 42

random.seed(RANDOM_SEED)
fake = Faker()
Faker.seed(RANDOM_SEED)

PROJECT_ROOT = Path(__file__).resolve().parents[1]
OUTPUT_DIRECTORY = PROJECT_ROOT / "data" / "generated_raw"
OUTPUT_FILE = OUTPUT_DIRECTORY / "shipments_raw_100000.csv"

PORTS = [
    {"country": "United States", "code": "US", "port": "Los Angeles"},
    {"country": "United States", "code": "US", "port": "New York"},
    {"country": "China", "code": "CN", "port": "Shanghai"},
    {"country": "China", "code": "CN", "port": "Shenzhen"},
    {"country": "India", "code": "IN", "port": "Mumbai"},
    {"country": "India", "code": "IN", "port": "Chennai"},
    {"country": "Netherlands", "code": "NL", "port": "Rotterdam"},
    {"country": "Singapore", "code": "SG", "port": "Singapore"},
    {"country": "Germany", "code": "DE", "port": "Hamburg"},
    {"country": "United Arab Emirates", "code": "AE", "port": "Jebel Ali"},
]

CARRIERS = [
    "OceanLink", "Pacific Cargo", "Global Freight", "Asia Logistics",
    "Maersk Global", "BlueWave Shipping", "CargoSphere", "NorthStar Logistics",
    "Evergreen Transit", "Atlas Freight",
]

CARGO_TYPES = [
    "Electronics", "Automotive Parts", "Medical Supplies", "Textiles",
    "Machinery", "Food Products", "Chemicals", "Consumer Goods",
]

COUNTRY_VARIANTS = {
    "United States": ["United States", "USA", "US", "U.S."],
    "China": ["China", "CHN", "PRC"],
    "India": ["India", "IND", "Republic of India"],
    "Netherlands": ["Netherlands", "NLD", "Holland"],
    "Singapore": ["Singapore", "SG", "SGP"],
    "Germany": ["Germany", "DE", "DEU"],
    "United Arab Emirates": ["United Arab Emirates", "UAE", "AE"],
}

STATUS_VARIANTS = {
    "Delivered": ["Delivered", "DELIVERED", "delivered", "Completed"],
    "Delayed": ["Delayed", "DELAYED", "delayed", "Late"],
    "In Transit": ["In Transit", "in_transit", "IN TRANSIT", "On Route"],
    "Cancelled": ["Cancelled", "CANCELLED", "cancelled"],
}


def dirty_country_name(country: str) -> str:
    """Return intentionally inconsistent country names."""
    return random.choice(COUNTRY_VARIANTS[country])


def dirty_status(status: str) -> str:
    """Return intentionally inconsistent shipment statuses."""
    return random.choice(STATUS_VARIANTS[status])


def dirty_date(date_value: pd.Timestamp) -> str:
    """Return mixed date formats to simulate raw operational data."""
    formats = ["%Y-%m-%d", "%d-%m-%Y", "%Y/%m/%d", "%m/%d/%Y"]
    return date_value.strftime(random.choice(formats))


def generate_shipment(row_number: int) -> dict:
    origin = random.choice(PORTS)
    destination = random.choice([port for port in PORTS if port != origin])

    shipment_date = pd.Timestamp(
        fake.date_between(start_date="-3y", end_date="today")
    )
    transit_days = random.randint(12, 45)
    expected_delivery = shipment_date + pd.Timedelta(days=transit_days)

    outcome = random.choices(
        ["Delivered", "Delayed", "In Transit", "Cancelled"],
        weights=[65, 18, 14, 3],
        k=1,
    )[0]

    actual_delivery = None
    if outcome == "Delivered":
        actual_delivery = expected_delivery + pd.Timedelta(
            days=random.randint(-3, 2)
        )
    elif outcome == "Delayed":
        actual_delivery = expected_delivery + pd.Timedelta(
            days=random.randint(3, 20)
        )

    cargo_value = round(random.uniform(5_000, 500_000), 2)

    record = {
        "shipment_id": f"SHP-{row_number:07d}",
        "origin_country": dirty_country_name(origin["country"]),
        "destination_country": dirty_country_name(destination["country"]),
        "origin_port": origin["port"],
        "destination_port": destination["port"],
        "shipment_date": dirty_date(shipment_date),
        "expected_delivery_date": dirty_date(expected_delivery),
        "actual_delivery_date": (
            dirty_date(actual_delivery) if actual_delivery is not None else ""
        ),
        "shipment_status": dirty_status(outcome),
        "cargo_type": random.choice(CARGO_TYPES),
        "cargo_value_usd": cargo_value,
        "carrier": random.choice(CARRIERS),
        "source_system": random.choice(["ERP", "TMS", "Partner Portal"]),
        "ingested_at": pd.Timestamp.now(tz="UTC").isoformat(),
    }

    # Intentional data-quality issues.
    if random.random() < 0.03:
        record["actual_delivery_date"] = ""
    if random.random() < 0.02:
        record["cargo_value_usd"] = ""
    if random.random() < 0.01:
        record["cargo_value_usd"] = -abs(cargo_value)
    if random.random() < 0.005:
        record["shipment_date"] = "invalid-date"

    return record


def main() -> None:
    OUTPUT_DIRECTORY.mkdir(parents=True, exist_ok=True)

    shipments = [generate_shipment(index) for index in range(1, NUMBER_OF_ROWS + 1)]

    # Add duplicate raw records intentionally.
    duplicate_records = random.sample(shipments, k=2_000)
    shipments.extend(duplicate_records)

    dataframe = pd.DataFrame(shipments)
    dataframe.to_csv(OUTPUT_FILE, index=False)

    print(f"Created: {OUTPUT_FILE}")
    print(f"Total raw rows: {len(dataframe):,}")
    print(f"Unique shipment IDs: {dataframe['shipment_id'].nunique():,}")


if __name__ == "__main__":
    main()
