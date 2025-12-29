from config.constants import COUNTRY_REGION_MAP

def normalize(value):
    return value.strip()

def map_customer_to_regions(customer, detected_regions):
    """
    Returns list of regions OR ['UNKNOWN']
    """
    # Rule 1: Subscribed Regions
    subscribed = customer.get("Subscribed Regions", "")
    if subscribed:
        regions = [normalize(r) for r in subscribed.split(",")]
        valid = [r for r in regions if r in detected_regions]
        return valid if valid else ["UNKNOWN"]

    # Rule 2: Country-based mapping
    country = customer.get("Country", "")
    region = COUNTRY_REGION_MAP.get(country)

    if region and region in detected_regions:
        return [region]

    # Rule 3: Unknown
    return ["UNKNOWN"]
