

from flask import Flask, request, jsonify
from datetime import date

from .services.services import finalizar_conn_cur, conn_cur
# from app import conn_cur, finalizar_conn_cur


app = Flask(__name__)




@app.route('/series', methods=['POST'])
def create():
    data = request.json
    conn, cur = conn_cur()
    data['serie'] = data['serie'].title()
    data['genre'] = data['genre'].title()
    cur.execute(
        """
            CREATE TABLE IF NOT EXISTS ka_series
                (
                    id BIGSERIAL PRIMARY KEY,
                    serie VARCHAR(100) NOT NULL UNIQUE,
                    seasons INTEGER NOT NULL,
                    released_date DATE NOT NULL,
                    genre VARCHAR(50) NOT NULL,
                    imdb_rating FLOAT NOT NULL
                );
            
            INSERT INTO ka_series
                (serie, seasons, released_date, genre, imdb_rating)
            VALUES
                (%(serie)s, %(seasons)s, %(released_date)s, %(genre)s, %(imdb_rating)s)
            RETURNING *;
            
        """,
        data,

    )

    query = cur.fetchone()
    
    table = ["id", "serie", "seasons", "released_date", "genre", "imdb_rating"]
    response = dict(zip(table, query))
    
    response['released_date'] =  response['released_date'].strftime("%d/%m/%y")
    finalizar_conn_cur(conn, cur)


    return jsonify(response), 201


@app.route('/series', methods=['GET'])
def series():
    conn, cur = conn_cur()

    cur.execute("SELECT * FROM ka_series")

    query = cur.fetchall()

    finalizar_conn_cur(conn, cur)

    table = ["id", "serie", "seasons", "released_date", "genre", "imdb_rating"]
    response = {"data": [dict(zip(table, data)) for data in query]}

    return jsonify(response)
    

@app.route('/series/<int:serie_id>', methods=['GET'])
def select_by_id(serie_id: str) -> dict:
    
    data = dict(zip(["id"], [serie_id]))
    
    
    conn, cur = conn_cur()

    cur.execute("""SELECT * FROM ka_series WHERE id = %(id)s""", data)
    query = cur.fetchall()
    
    if not query:
        return {"error": "Not Found"}

    table = ["id", "serie", "seasons", "released_date", "genre", "imdb_rating"]
    
    response = {"data": dict(zip(table, data)) for data in query}
    finalizar_conn_cur(conn, cur)
    response['data']['released_date'] = response['data']['released_date'].strftime("%d/%m/%y")
    return jsonify(response)