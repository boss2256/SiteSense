from urllib.parse import urlparse
import geoip2.database
import socket


def clean_url(url):
    parsed = urlparse(url, scheme="http")  # Default to "http" if no scheme is provided
    if not parsed.netloc:
        parsed = urlparse(f"http://{url}")
    return parsed.geturl()


def get_geoip_location(url):
    domain = urlparse(url).netloc.replace("www.", "")

    try:
        # Resolve domain to IP address
        ip_address = socket.gethostbyname(domain)
    except socket.gaierror:
        return {"error": "Domain name could not be resolved to an IP address."}

    with geoip2.database.Reader('geoip_data/GeoLite2-City.mmdb') as reader:
        try:
            # Perform GeoIP lookup
            response = reader.city(ip_address)
            return {
                "country": response.country.name,
                "region": response.subdivisions.most_specific.name,
                "city": response.city.name
            }
        except geoip2.errors.AddressNotFoundError:
            return {"error": "IP address location data not found in GeoLite2 database."}
