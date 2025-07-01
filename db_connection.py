import psycopg2
import psycopg2.extras
import json

def connect_to_db():
    try:
        conn_db = psycopg2.connect(
            dbname = 'postgres',
            user = 'postgres.vaovpjmauusqikstnrcp',
            password = 'BIDzr0xi90cUuJSO',
            host = 'aws-0-eu-north-1.pooler.supabase.com',
            port = '6543'
        )
        print("Uspjesno povezan na bazu.")
        return  conn_db
    except Exception as e:
        print(f'Greska pri povezivanju: {e}.')
        return None

connect_to_db()


def execute_query(query, params=None):
    try:
        conn = connect_to_db()
        if conn is None:
            return None

        cur = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
        if params:
            cur.execute(query, params)
        else:
            cur.execute(query)
        rows = cur.fetchall()

        # Za svaki red, ako postoji kolona 'location' koja je string GeoJSON,
        # pretvori je u python dict da bi JSON jsonify lepo to prosledio
        for row in rows:
            if 'geom' in row and row['geom']:
                row['geom'] = json.loads(row['geom'])

        cur.close()
        conn.close()
        return rows
    except Exception as e:
        print(f"Greska pri izvrsavanju upita: {e}")
        return None


