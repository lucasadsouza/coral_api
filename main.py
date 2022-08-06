import pymysql
from app import app
from db_config import mysql
from flask import jsonify, flash, request, send_from_directory
from flask_cors import cross_origin




def handleResp(method, statusCode, reqName=None, body=None):
    if method == 'get' and body:
        response = jsonify(body)

    elif method == 'post' and reqName:
        response = jsonify('{0} added successfully!'.format(reqName.capitalize()))

    elif method == 'put' and reqName:
        response = jsonify('{0} updated successfully!'.format(reqName.capitalize()))

    elif method == 'delete' and reqName:
        response = jsonify('{0} deleted successfully!'.format(reqName.capitalize()))


    response.status_code = statusCode

    return response


def handleMySql(action, values=None, get=None, fetchAll=True):
    conn = mysql.connect()
    if get:
        cursor = conn.cursor(pymysql.cursors.DictCursor)
    else:
        cursor = conn.cursor()

    if values:
        cursor.execute(action, values)
    else:
        cursor.execute(action)
        
    if get:
        if fetchAll:
            rows = cursor.fetchall()

        else:
            rows = cursor.fetchone()

        cursor.close()
        conn.close()

        return rows

    else:
        conn.commit()

        cursor.close()
        conn.close()
        
        
def handleGamesGenres(gamesRows):
    games = []
    for gameRow in gamesRows:
        genresRows = handleMySql(
            "select gr.label as genre from genres gr inner join games_genres gg on gg.genre_id = gr.id inner join games g on gg.game_id = g.id where g.id = %s",
            gameRow['id'], get=True
        )

        gameGenres = []
        for genreRow in genresRows:
            gameGenres.append(genreRow['genre'])

        gameRow['genres'] = gameGenres
        games.append(gameRow)
    
    return games




# USER REQUESTS
@app.route('/users', methods=['POST'])
@cross_origin()
def add_user():
    try:
        _json = request.json
        _name = _json['nickname']
        _token = _json['token']
        _age = _json['age']

        if _name and _token and _age and request.method == 'POST':
            handleMySql("insert into users (nickname, token, age) values (%s, %s, %s)", (_name, _token, _age))

            return handleResp('post', 200, reqName='User')

        else:
            return not_found()

    except Exception as err:
        print(err)


@app.route('/users', methods=['GET'])
@cross_origin()
def users():
    try:
        if request.method == 'GET':            
            rows = handleMySql("select * from users", get=True)

            return handleResp('get', 200, body=rows)

        else:
            return not_found()
    
    except Exception as err:
        print(err)


@app.route('/users/<token>', methods=['GET'])
@cross_origin()
def user(token):
    try:
        if token and request.method == 'GET':
            row = handleMySql("select * from users where token=%s", token, get=True, fetchAll=False)

            if row == None:
                return not_found()

            else:
                return handleResp('get', 200, body=row)

        else:
            return not_found()

    except Exception as err:
        print(err)


@app.route('/users/<token>', methods=['PUT'])
@cross_origin()
def update_user(token):
    try:
        _json = request.json
        _name = _json['nickname']
        _age = _json['age']

        if token and _name and _age and request.method == 'PUT':
            handleMySql("update users set nickname=%s, age=%s where token=%s", (_name, _age, token))

            return handleResp('put', 200, reqName='User')

        else:
            return not_found()

    except Exception as err:
        print(err)


@app.route('/users/<token>', methods=['DELETE'])
@cross_origin()
def delete_user(token):
    try:
        if token and request.method == 'DELETE':
            handleMySql("delete from users where token=%s", token)

            return handleResp('delete', 200, reqName='User')

        else:
            return not_found()

    except Exception as err:
        print(err)




# GENRE LIST REQUESTS
@app.route('/genres', methods=['GET'])
@cross_origin()
def genres():
    try:
        if request.method == 'GET':
            rows = handleMySql("select * from genres", get=True)

            return handleResp('get', 200, body=rows)

        else:
            return not_found()

    except Exception as err:
        print(err)




# GAME LIST REQUESTS
@app.route('/games', methods=['GET'])
@cross_origin()
def games():
    try:
        if request.method == 'GET':
            gamesRows = handleMySql("select * from games", get=True)
                
            games = handleGamesGenres(gamesRows)

            return handleResp('get', 200, body=games)

        else:
            return not_found()

    except Exception as err:
        print(err)


@app.route('/games/<int:g_id>')
@cross_origin()
def game(g_id):
    try:
        if g_id and request.method == 'GET':
            gamesRows = handleMySql("select * from games where id=%s", g_id, get=True)

            if gamesRows == ():
                return not_found()

            else:
                games = handleGamesGenres(gamesRows)

                return handleResp('get', 200, body=games)

        else:
            return not_found()

    except Exception as err:
        print(err)




# USER GAME LIST REQUESTS
@app.route('/users/<token>/games', methods=['GET'])
@cross_origin()
def user_games(token):
    try:
        if token and request.method == 'GET':
            gamesRows = handleMySql(
                "select g.*, sg.id as g_status, ug.rating as rating from games g inner join users_games ug on ug.game_id = g.id inner join users u on ug.user_id = u.id inner join status sg on ug.status_id = sg.id where u.token = %s",
                token, get=True
            )

            if gamesRows == ():
                return not_found()

            games = handleGamesGenres(gamesRows)

            return handleResp('get', 200, body=games)

        else:
            return not_found()

    except Exception as err:
        print(err)


@app.route('/users/<token>/games/<int:g_id>', methods=['GET'])
@cross_origin()
def user_game(token, g_id):
    try:
        if token and g_id and request.method == 'GET':
            gamesRows = handleMySql(
                "select g.*, sg.id as g_status, ug.rating as rating from games g inner join users_games ug on ug.game_id = g.id inner join users u on ug.user_id = u.id inner join status sg on ug.status_id = sg.id where u.token = %s and g.id = %s",
                (token, g_id), get=True
            )

            if gamesRows == ():
                return not_found()

            games = handleGamesGenres(gamesRows)

            return handleResp('get', 200, body=games)

        else:
            return not_found()

    except Exception as err:
        print(err)


@app.route('/users/<token>/games', methods=['POST'])
@cross_origin()
def add_user_game(token):
    try:
        _json = request.json
        _gameId = _json['game']
        _status = _json['status']
        _rating = _json['rating']

        if _rating and _status and token and _gameId and request.method == 'POST':
            userId = handleMySql("select id from users where token = %s", token, get=True)[0]['id']

            handleMySql(
                "insert into users_games (status_id, game_id, user_id, rating) values (%s, %s, %s, %s)",
                (_status, _gameId, userId, _rating - 1)
            )
            

            return handleResp('post', 200, reqName='Game')

        else:
            return not_found()

    except Exception as err:
        print(err)


@app.route('/users/<token>/games/<int:g_id>', methods=['PUT'])
@cross_origin()
def update_user_game(token, g_id):
    try:
        _json = request.json
        _status = _json['status']
        _rating = _json['rating']

        if _rating and _status and token and g_id and request.method == 'PUT':
            userId = handleMySql("select id from users where token = %s", token, get=True)[0]['id']

            handleMySql(
                "update users_games set status_id = %s, rating = %s where game_id = %s and user_id = %s",
                (_status, _rating - 1, g_id, userId)
            )

            return handleResp('put', 200, reqName='User game')

        else:
            return not_found()

    except Exception as err:
        print(err)


@app.route('/users/<token>/games/<int:g_id>', methods=['DELETE'])
@cross_origin()
def delete_user_game(token, g_id):
    try:
        if token and g_id and request.method == 'DELETE':
            userId = handleMySql("select id from users where token = %s", token, get=True)[0]['id']

            handleMySql("delete from users_games where game_id = %s and user_id = %s", (g_id, userId))

            return handleResp('delete', 200, reqName='User game')

        else:
            return not_found()

    except Exception as err:
        print(err)




# IMAGES



@app.route('/images/<path:i_name>', methods=['GET'])
@cross_origin()
def image(i_name):
    try:
        if i_name and request.method == 'GET':
            return send_from_directory('images', i_name)

        else:
            return not_found()

    except Exception as err:
        print(err)


@app.route('/images/games/<path:i_name>', methods=['GET'])
@cross_origin()
def game_image(i_name):
    try:
        if i_name and request.method == 'GET':
            return send_from_directory('images/games', i_name)

        else:
            return not_found()

    except Exception as err:
        print(err)


@app.route('/images/users/<int:token>', methods=['GET'])
@cross_origin()
def user_image(token):
    try:
        if token and request.method == 'GET':
            return send_from_directory('images/users_profile_pictures', token)

        else:
            return not_found()

    except Exception as err:
        print(err)


@app.route('/images/games', methods=['POST'])
@cross_origin()
def add_game_image(token):
    try:
        _json = request.json
        _gameId = _json['game']
        _status = _json['status']
        _rating = _json['rating']

        if _rating and _status and token and _gameId and request.method == 'POST':
            userId = handleMySql("select id from users where token = %s", token, get=True)[0]['id']

            handleMySql(
                "insert into users_games (status_id, game_id, user_id, rating) values (%s, %s, %s, %s)",
                (_status, _gameId, userId, _rating)
            )
            

            return handleResp('post', 200, reqName='Game')

        else:
            return not_found()

    except Exception as err:
        print(err)


@app.route('/images/games/<int:g_id>', methods=['PUT'])
@cross_origin()
def update_game_image(token, g_id):
    try:
        _json = request.json
        _status = _json['status']
        _rating = _json['rating']

        if _rating and _status and token and g_id and request.method == 'PUT':
            userId = handleMySql("select id from users where token = %s", token, get=True)[0]['id']

            handleMySql(
                "update users_games set status_id = %s, rating = %s where game_id = %s and user_id = %s",
                (_status, _rating, g_id, userId)
            )

            return handleResp('put', 200, reqName='User game')

        else:
            return not_found()

    except Exception as err:
        print(err)


@app.route('/images/games/<int:g_id>', methods=['DELETE'])
@cross_origin()
def delete_game_image(token, g_id):
    try:
        if token and g_id and request.method == 'DELETE':
            userId = handleMySql("select id from users where token = %s", token, get=True)[0]['id']

            handleMySql("delete from users_games where game_id = %s and user_id = %s", (g_id, userId))

            return handleResp('delete', 200, reqName='User game')

        else:
            return not_found()

    except Exception as err:
        print(err)




# ERROR HANDLERS
@app.errorhandler(404)
def not_found(error=None):
    message = {
        'status': 404,
        'message': 'Not Found: ' + request.url
    }

    return handleResp('get', 404, body=message)


if __name__ == '__main__':
    app.run()
