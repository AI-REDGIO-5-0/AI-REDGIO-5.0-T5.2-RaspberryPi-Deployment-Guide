import requests
import sys

REST_ENDPOINT = "http://localhost:5000/api/battery"


def check_battery():
    print(f"Querying battery status from: {REST_ENDPOINT}\n")
    try:
        response = requests.get(REST_ENDPOINT)
        response.raise_for_status()
        data = response.json()

        print("Battery API Response:")
        for key, value in data.items():
            print(f"  {key}: {value}")

    except requests.exceptions.ConnectionError:
        print("Could not connect to the REST API. Is it running?")
        sys.exit(1)
    except requests.exceptions.HTTPError as e:
        print(f"HTTP error: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"Unexpected error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    check_battery()