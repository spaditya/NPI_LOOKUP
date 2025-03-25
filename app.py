# 
from flask import Flask, render_template, request, jsonify
import requests

# Create the Flask app
app = Flask(__name__)

# Route for Home page which renders the HTML template
@app.route("/")
def home():
    return render_template("index.html")

# Set up for the Seach route
@app.route("/search", methods=["GET"])
def search():
    # Gets input from the search bar and the type from the dropdown
    query = request.args.get("query")
    search_type = request.args.get("type")

    # If the input is empty, return an error message
    if not query:
        return jsonify({"error": "Please enter a search query"}), 400

    # This dictionary converts the search type to the API parameter
    search_param_map = {
        "npi": "number",
        "first_name": "first_name",
        "last_name": "last_name",
        "organization": "organization_name"
    }

    # If input is invalid, return an error message
    if search_type not in search_param_map:
        return jsonify({"error": "Invalid search type"}), 400

    # Make the request to the NPPES NPI Registry API
    response = requests.get("https://npiregistry.cms.hhs.gov/api/", params={
        "version": "2.1",
        search_param_map[search_type]: query
    })

    data = response.json()

    # Return an error if no providers found
    if not data.get("results"):
        return jsonify({"error": "No results found"}), 404

    # Creates an empty list to store the results
    results = []

    # Loop through the results from the API
    for provider in data["results"]:
        basic_info = provider.get("basic", {})

        # Get provider name
        if "organization_name" in basic_info:
            name = basic_info.get("organization_name", "N/A")
        # If the provider is an individual, get first and last name
        else:
            first = basic_info.get("first_name", "")
            last = basic_info.get("last_name", "")
            name = f"{first} {last}".strip() or "N/A"

        # Get taxonomy
        taxonomy_list = provider.get("taxonomies", [])
        taxonomy = taxonomy_list[0]["desc"] if taxonomy_list else "N/A"

        # Get location
        address_list = provider.get("addresses", [])
        if address_list:
            city = address_list[0].get("city", "N/A")
            state = address_list[0].get("state", "N/A")
            location = f"{city}, {state}"
        else:
            location = "N/A"

        # Appends the provider information to results list
        results.append({
            "NPI": provider.get("number", "N/A"),
            "Name": name,
            "Taxonomy": taxonomy,
            "Location": location
        })

    # Return list of provider results
    return jsonify(results)

# Run the app
if __name__ == "__main__":
    app.run(debug=True)