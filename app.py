from flask import Flask, request, jsonify
from scraper.scraper import scrape_ihk_data
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

        # Return the scraped data as JSON
        return jsonify({
            "message": "Data scraped successfully",
            "data": scraped_data
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True)