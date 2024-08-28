from flask import Flask, request, jsonify
from scraper.scraper import scrape_ihk_data
from collections import OrderedDict
import json

app = Flask(__name__)

@app.route('/scrape-ihk', methods=['POST'])
def scrape_ihk():
    data = request.json
    url = data.get('url')

    if not url:
        return jsonify({"error": "URL is required"}), 400

    try:
        # Scrape data from the provided URL
        scraped_data = scrape_ihk_data(url)

        # Chuyển đổi kết quả sang OrderedDict để bảo toàn thứ tự
        ordered_data = [OrderedDict([
            ("Angebots-Nr.", item.get("Angebots-Nr.")),
            ("Stellenbeschreibung", item.get("Stellenbeschreibung")),
            ("Schulabschluss wünschenswert", item.get("Schulabschluss wünschenswert")),
            ("gewünschte Vorqualifikation", item.get("gewünschte Vorqualifikation")),
            ("Beginn", item.get("Beginn")),
            ("Angebotene Plätze", item.get("Angebotene Plätze")),
            ("Adresse", item.get("Adresse")),
            ("Telefon", item.get("Telefon")),
            ("Email", item.get("Email")),
            ("Weitere Ausbildungsplatzangebote", item.get("Weitere Ausbildungsplatzangebote")),
            ("URL", item.get("URL"))
        ]) for item in scraped_data]

        # Return the scraped data with correct order using json.dumps
        return app.response_class(
            response=json.dumps({"message": "Data scraped successfully", "data": ordered_data}, ensure_ascii=False),
            mimetype='application/json'
        )
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True)