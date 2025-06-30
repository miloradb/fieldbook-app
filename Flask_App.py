from flask import Flask, jsonify
from db_connection import execute_query
from flask_cors import CORS

app = Flask(__name__)
CORS(app)


@app.route('/')

def index():
    #query = 'SELECT id, interni_broj, katastarska_opstina, ST_AsGeoJSON(geom) as geom FROM parcele;'
    get_parcele_query = 'SELECT id, interni_broj, katastarska_cestica, katastarska_opstina, potez, vlasnik_zemljista, udio_u_vlasnickoj_strukturi, nacin_koriscenja, klasa_zemljista, povrsina, napomena, ST_AsGeoJSON(ST_Transform(geom, 4326)) as geom FROM parcele;'

    rows = execute_query(get_parcele_query)
    if not rows:
        return jsonify({"error": "No data found"})

    features = []
    for row in rows:
        features.append({
            "type": "Feature",
            "geometry": row.get("geom"),
            "properties": {
                "id": row["id"],
                "broj": row["interni_broj"],
                "kc": row["katastarska_cestica"],
                "opstina": row["katastarska_opstina"],
                "potez": row["potez"],
                "vlasnik": row["vlasnik_zemljista"],
                "udio": row["udio_u_vlasnickoj_strukturi"],
                "nacin": row["nacin_koriscenja"],
                "klasa": row["klasa_zemljista"],
                "povrsina": row["povrsina"],
                "napomena": row["napomena"]
            }
        })

    return jsonify({
        "type": "FeatureCollection",
        "features": features
    })

@app.route('/plodored')

def plodored():
    get_plodored_query = 'SELECT id, parcela_id, godina, kultura, napomena FROM plodored'
    rows1 = execute_query(get_plodored_query)
    if not rows1:
        return jsonify({"error": "No data found"})

    features1 = []
    for plodored in rows1:
        features1.append({
            "type": "Feature",
            "properties": {
                "id": plodored["id"],
                "parcela_id": plodored["parcela_id"],
                "godina": plodored["godina"],
                "kultura": plodored["kultura"],
                "napomena": plodored["napomena"]
            }
        })

    return jsonify({
        "type": "Feature",
        "features": features1
    })


@app.route('/plodored/<int:parcela_id>')
def plodored_by_parcela(parcela_id):
    # Ubaci vrednost direktno u string - pazi da je int i dolazi od Flask konverzije, pa je relativno sigurno
    query_parcela_id = f'SELECT id, parcela_id, godina, kultura, napomena FROM plodored WHERE parcela_id = {parcela_id}'

    rows2 = execute_query(query_parcela_id)
    if not rows2:
        return jsonify({"error": "Podaci nisu pronadjeni"})

    return jsonify(rows2)


if __name__ == "__main__":
    app.run(debug=True)
