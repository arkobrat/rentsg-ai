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
	with open(json_file, mode="w", encoding="utf-8") as f:
		json.dump(rows, f, indent=4, ensure_ascii=False)
	print(f"Converted {csv_file} to {json_file}")

if __name__ == "__main__":
	csv_to_json(
		os.path.abspath(os.path.join(os.path.dirname(__file__), "propertyguru_listings.csv")),
		os.path.abspath(os.path.join(os.path.dirname(__file__), "propertyguru_listings.json"))
	)
