"""
web_app.py - Main Flask web application for serving the beer dataset.
Provides a REST API endpoint for the frontend to fetch joined data from Vinmonopolet and Untappd.
"""
from flask import Flask, jsonify, send_from_directory
import sqlite3
import os

app = Flask(__name__, static_folder='static', static_url_path='')
DB_PATH = "vmp_untappd_new.db"

@app.route('/')
def index():
    return send_from_directory('static', 'index.html')

@app.route('/api/beers')
def get_beers():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cur = conn.cursor()
    
    query = """
    SELECT 
        v.product_id_vmp,
        v.name as vmp_name,
        pr.name as vmp_brewery,
        pr.country as vmp_country,
        c.category_main as vmp_main_category,
        c.category_sub as vmp_style,
        u.beer_style as unt_style,
        v.vintage,
        v.price,
        v.volume_ml,
        v.abv as vmp_abv,
        v.selection,
        v.packaging,
        v.aroma,
        v.taste,
        v.color,
        v.method,
        v.allergens,
        v.url_vmp,
        v.url_image as vmp_image,
        v.is_discontinued,
        v.match_confidence,
        u.beer_name as unt_name,
        ub.brewery_name as unt_brewery,
        u.beer_abv as unt_abv,
        '' as unt_description,
        u.beer_ibu as unt_ibu,
        u.rating_score,
        u.rating_count,
        u.beer_url as url_unt,
        u.beer_label as url_image,
        u.last_synced_unt
    FROM vmp_products v
    LEFT JOIN vmp_producers pr ON v.producer_id = pr.id
    LEFT JOIN vmp_categories c ON v.category_id = c.id
    LEFT JOIN unt_beers u ON v.bid = u.bid
    LEFT JOIN unt_beer_brewery_links ubbl ON u.bid = ubbl.bid
    LEFT JOIN unt_breweries ub ON ubbl.brewery_id = ub.brewery_id
    """
    
    cur.execute(query)
    rows = cur.fetchall()
    conn.close()
    
    beers = [dict(row) for row in rows]
    return jsonify(beers)

if __name__ == '__main__':
    app.run(debug=True, port=5000)
