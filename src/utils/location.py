from typing import Dict
from PIL.ExifTags import TAGS, GPSTAGS
from PIL import Image
import requests
from src.config import GOOGLE_MAPS_API_KEY, ACCEPTED_CITY


def get_address(file_path: str) -> Dict[str, str]:
    """
    Extract GPS coordinates from image EXIF data and get address using Google Maps API.
    Returns an address dictionary if the image contains valid GPS data and is in the accepted city.
    """
    try:
        print(f"Processing file: {file_path}")

        with Image.open(file_path) as img:
            exif = img._getexif()
            if not exif:
                print("No EXIF data found.")
                return {}

            # Extract GPS info
            gps_info = {}
            for tag, value in exif.items():
                decoded_tag = TAGS.get(tag, tag)
                if decoded_tag == "GPSInfo":
                    gps_info = {GPSTAGS.get(t, t): v for t, v in value.items()}

            if not gps_info:
                print("No GPS info found in EXIF data.")
                return {}

            print(f"Extracted GPS Info: {gps_info}")

            # Ensure required GPS tags are present
            required_keys = {
                "GPSLatitude",
                "GPSLatitudeRef",
                "GPSLongitude",
                "GPSLongitudeRef",
            }
            if not required_keys.issubset(gps_info):
                print(f"Missing required GPS keys: {required_keys - gps_info.keys()}")
                return {}

            # Convert GPS coordinates to decimal
            def convert_to_decimal(coord, ref):
                if not isinstance(coord, (list, tuple)) or len(coord) != 3:
                    print(f"Invalid coordinate format: {coord}")
                    return None
                degrees, minutes, seconds = coord
                decimal = degrees + minutes / 60 + seconds / 3600
                if ref in ["S", "W"]:  # South/West are negative
                    decimal *= -1
                return decimal

            latitude = convert_to_decimal(
                gps_info["GPSLatitude"], gps_info["GPSLatitudeRef"]
            )
            longitude = convert_to_decimal(
                gps_info["GPSLongitude"], gps_info["GPSLongitudeRef"]
            )

            if latitude is None or longitude is None:
                print("Failed to convert GPS coordinates.")
                return {}

            print(
                f"Converted Coordinates: Latitude = {latitude}, Longitude = {longitude}"
            )

            # Query Google Maps API
            response = requests.get(
                "https://maps.googleapis.com/maps/api/geocode/json",
                params={
                    "latlng": f"{latitude},{longitude}",
                    "key": GOOGLE_MAPS_API_KEY,
                    "language": "zh-tw",
                    "result_type": "street_address",
                },
                timeout=10,
            ).json()

            print(f"Google Maps API Response: {response}")

            if response.get("status") != "OK":
                print(f"Google Maps API Error: {response.get('status')}")
                return {}

            # Process results
            result = response["results"][0]
            address = {
                "street_number": "",
                "route": "",
                "postal_code": "",
                "country": "",
                "city": "",
                "district": "",
                "neighborhood": "",
            }

            # Map address components
            component_mapping = {
                "street_number": "street_number",
                "route": "route",
                "postal_code": "postal_code",
                "country": "country",
                "administrative_area_level_1": "city",
                "administrative_area_level_2": "district",
                "administrative_area_level_3": "neighborhood",
            }

            for comp in result["address_components"]:
                for t in comp["types"]:
                    if t in component_mapping:
                        key = component_mapping[t]
                        value = comp["long_name"]
                        if t == "street_number" and "號" in value:
                            value = value[: value.index("號") + 1]
                        address[key] = value

            address["formatted_address"] = (
                f"{address['postal_code']} {address['country']}{address['city']}"
                f"{address['district']}{address['neighborhood']}{address['route']}"
                f"{address['street_number']}"
            )

            if address.get("city") != ACCEPTED_CITY:
                print(f"Address is outside accepted city ({ACCEPTED_CITY}): {address}")
                return {}

            print(f"Final Address: {address}")
            return address

    except Exception as e:
        print(f"Error: {e}")
        return {}


if __name__ == "__main__":
    print(get_address("data/original/IMG_2430.jpeg"))
