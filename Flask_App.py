from flask import Flask, jsonify, request, send_from_directory
import json
from db_connection import execute_query, psycopg2
from flask_cors import CORS
from db_connection import connect_to_db

app = Flask(__name__, static_folder='.', static_url_path='')
CORS(app)


# Ruta za root (početnu stranicu)
@app.route('/')
def serve_index():
    return send_from_directory('.', 'login.html')
    
# Ruta za ostale statičke fajlove (css, js...)
@app.route('/<path:path>')
def serve_static(path):
    return send_from_directory('.', path)

@app.route('/field-book/<int:user_id>')
def field_book(user_id):
    get_user_query = (
        'SELECT id, interni_broj, katastarska_cestica, katastarska_opstina, potez, vlasnik_zemljista, '
        'udio_u_vlasnickoj_strukturi, nacin_koriscenja, klasa_zemljista, povrsina, napomena, user_id,'
        ' ST_AsGeoJSON(ST_Transform(geom, 4326)) as geom '
                      'FROM parcele '
                      'where user_id = %s;'
    )

    rows = execute_query(get_user_query, (user_id,))
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
                "napomena": row["napomena"],
                "user_id": row["user_id"]
            }
        })

    return jsonify({
        "type": "FeatureCollection",
        "features": features
    })





@app.route('/login', methods=['POST'])
def login():
    data = request.get_json()

    if not data or 'username' not in data or 'password' not in data:
        return jsonify({'error:': 'Nedostaju podaci'}), 400

    username = data['username']
    password = data['password']

    #Pronadji korisnika u bazi po username
    login_query = f'Select id, username, password, full_name FROM users WHERE username = %s'

    try:
        conn = connect_to_db()
        if conn is None:
            return jsonify({'error': 'Konekcija sa bazom nije uspjela'}), 500

        cur = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
        cur.execute(login_query, (username,))
        user = cur.fetchone()

        cur.close()
        conn.close()

        if user is None:
            return jsonify({"error": "Nepostojeci korisnik"}), 404

        if user['password'] != password:
            return jsonify({"error": "Pogresna lozinka"}), 401
            #print("Pogreska lozinka")

        #Uspjesan login - saljemo osnovne podatke
        return jsonify ({
            "message": "Uspjesno logovanje",
            "user_id": user['id'],
            "username": user["username"],
            "full_name": user["full_name"]
        })

    except Exception as e:
        print("Greska prilikom login-a", e)
        return jsonify({"error": "Greska na serveru"}), 500



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
        "type": "FeatureCollection",
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

@app.route('/korisnici')
def korisnici():
    query_korisnici = 'SELECT username, password, full_name, email FROM users'
    rows3 = execute_query(query_korisnici)
    if not rows3:
        return jsonify({"error": "Korisnici nisu pronadjeni"})
    return jsonify(rows3)



@app.route('/field-book')

def index():
    #query = 'SELECT id, interni_broj, katastarska_opstina, ST_AsGeoJSON(geom) as geom FROM parcele;'
    get_parcele_query = 'SELECT id, interni_broj, katastarska_cestica, katastarska_opstina, potez, vlasnik_zemljista, udio_u_vlasnickoj_strukturi, nacin_koriscenja, klasa_zemljista, povrsina, napomena, user_id, ST_AsGeoJSON(ST_Transform(geom, 4326)) as geom FROM parcele;'

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
                "povrsina": round(row["povrsina"], 2)
                "napomena": row["napomena"],
                "user_id": row["user_id"]
            }
        })

    return jsonify({
        "type": "FeatureCollection",
        "features": features
    })



if __name__ == "__main__":
    app.run(debug=True)
