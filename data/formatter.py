import csv
import os
import json

def csv_to_json(csv_file, json_file):
	with open(csv_file, mode="r", encoding="utf-8") as f:
		reader = csv.DictReader(f)
		rows = []
		import re
		for row in reader:
			title = row.get("Title", "")
			if title.startswith("For Rent - "):
				row["Title"] = title[len("For Rent - "):]
			# Extract dollar value from Price
			price = row.get("Price", "")
			price_match = re.search(r"\$\s*([\d,]+)", price)
			if price_match:
				row["Price"] = price_match.group(1).replace(",", "")
			else:
				row["Price"] = ""
			# Extract dollar value from Price per sqft
			ppsf = row.get("Price per sqft", "")
			ppsf_match = re.search(r"\$\s*([\d.]+)", ppsf)
			if ppsf_match:
				row["Price per sqft"] = ppsf_match.group(1)
			else:
				row["Price per sqft"] = ""
			# Extract number from Bedrooms
			bedrooms = row.get("Bedrooms", "")
			bedrooms_match = re.search(r"(\d+)", bedrooms)
			if bedrooms_match:
				row["Bedrooms"] = bedrooms_match.group(1)
			else:
				row["Bedrooms"] = ""
			# Extract number from Bathrooms
			bathrooms = row.get("Bathrooms", "")
			bathrooms_match = re.search(r"(\d+)", bathrooms)
			if bathrooms_match:
				row["Bathrooms"] = bathrooms_match.group(1)
			else:
				row["Bathrooms"] = ""
			# Extract number from Floor Area
			floor_area = row.get("Floor Area", "")
			floor_area_match = re.search(r"([\d,.]+)", floor_area)
			if floor_area_match:
				row["Floor Area"] = floor_area_match.group(1).replace(",", "")
			else:
				row["Floor Area"] = ""
			rows.append(row)
	# Group by Title and aggregate fields
	grouped = {}
	for row in rows:
		title = row.get("Title", "")
		price = row.get("Price", "")
		url = row.get("URL", "")
		image_url = row.get("ImageURL", "")
		address = row.get("Address", "")
		location = row.get("Location", "")
		bedrooms = row.get("Bedrooms", "")
		bathrooms = row.get("Bathrooms", "")
		floor_area = row.get("Floor Area", "")
		ppsf = row.get("Price per sqft", "")
		if title not in grouped:
			grouped[title] = {
				"Title": title,
				"URLs": [url] if url else [],
				"ImageURL": image_url,
				"Addresses": [address] if address else [],
				"Location": location,
				"Prices": [int(price)] if price.isdigit() else [],
				"Bedrooms": [int(bedrooms)] if bedrooms.isdigit() else [],
				"Bathrooms": [int(bathrooms)] if bathrooms.isdigit() else [],
				"Floor Area": [float(floor_area)] if floor_area.replace('.', '', 1).isdigit() else [],
				"Price per sqft": [float(ppsf)] if ppsf.replace('.', '', 1).isdigit() else [],
			}
		else:
			if url:
				grouped[title]["URLs"].append(url)
			if address:
				grouped[title]["Addresses"].append(address)
			if price.isdigit():
				grouped[title]["Prices"].append(int(price))
			if bedrooms.isdigit():
				grouped[title]["Bedrooms"].append(int(bedrooms))
			if bathrooms.isdigit():
				grouped[title]["Bathrooms"].append(int(bathrooms))
			if floor_area.replace('.', '', 1).isdigit():
				grouped[title]["Floor Area"].append(float(floor_area))
			if ppsf.replace('.', '', 1).isdigit():
				grouped[title]["Price per sqft"].append(float(ppsf))
	# Prepare output with ranges
	output = []
	for title, data in grouped.items():
		def make_range(values):
			if values:
				return {"min": min(values), "max": max(values)}
			else:
				return {"min": None, "max": None}
		output.append({
			"Title": title,
			"URLs": data["URLs"],
			"ImageURL": data["ImageURL"],
			"Addresses": list(set(data["Addresses"])),
			"Location": data["Location"],
			"Price Range": make_range(data["Prices"]),
			"Bedrooms Range": make_range(data["Bedrooms"]),
			"Bathrooms Range": make_range(data["Bathrooms"]),
			"Floor Area Range": make_range(data["Floor Area"]),
			"Price per sqft Range": make_range(data["Price per sqft"])
		})
	with open(json_file, mode="w", encoding="utf-8") as f:
		json.dump(output, f, indent=4, ensure_ascii=False)
	print(f"Converted {csv_file} to {json_file} (grouped by Title, aggregated URLs, addresses, ranges for numeric fields)")

if __name__ == "__main__":
	csv_to_json(
		os.path.abspath(os.path.join(os.path.dirname(__file__), "propertyguru_listings.csv")),
		os.path.abspath(os.path.join(os.path.dirname(__file__), "propertyguru_listings.json"))
	)
