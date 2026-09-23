"""
web_app.py - Main Flask web application for serving the beer dataset.
Provides a REST API endpoint for the frontend to fetch joined data from Vinmonopolet and Untappd.
"""
from flask import Flask, jsonify, send_from_directory
import sqlite3
import os

app = Flask(__name__, static_folder='static', static_url_path='')

# Use absolute path for the database so it works properly on servers like PythonAnywhere
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(BASE_DIR, "vmp_untappd_new.db")

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
        -- VMP Products (Base)
        v.product_id_vmp,
        v.bid as unt_id,
        v.match_confidence,
        v.producer_id as vmp_producer_id,
        v.category_id as vmp_category_id,
        v.name as vmp_name,
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

        -- VMP Producers
        pr.name as vmp_brewery,
        pr.country as vmp_country,
        
        -- VMP Categories
        c.category_main as vmp_main_category,
        c.category_sub as vmp_style,
        
        -- Untappd Beers
        u.beer_name as unt_name,
        u.style_id as unt_style_id,
        u.beer_abv as unt_abv,
        u.beer_ibu as unt_ibu,
        u.is_beer as unt_is_beer,
        u.rating_score,
        u.rating_count,
        u.popularity,
        u.in_production,
        u.has_community_award,
        u.community_awards,
        u.index_date,
        u.beer_url as url_unt,
        u.beer_label as url_image,
        u.last_synced_unt,
        
        -- Untappd Styles
        us.name as unt_style,
        us.description as unt_style_description,
        
        -- Untappd Breweries
        ub.brewery_id as unt_brewery_id,
        ub.brewery_name as unt_brewery,
        ub.brewery_url,
        ub.brewery_label,
        ub.lat as unt_lat,
        ub.lng as unt_lng
        
    FROM vmp_products v
    LEFT JOIN vmp_producers pr ON v.producer_id = pr.id
    LEFT JOIN vmp_categories c ON v.category_id = c.id
    LEFT JOIN unt_beers u ON v.bid = u.bid
    LEFT JOIN unt_styles us ON u.style_id = us.id
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
