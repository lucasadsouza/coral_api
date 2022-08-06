from app import app
from flaskext.mysql import MySQL
from flask_cors import CORS


mysql = MySQL()

cors = CORS(app)

# MySQL configurations
# app.config['MYSQL_DATABASE_USER'] = 'root'
# app.config['MYSQL_DATABASE_PASSWORD'] = '1234'
# app.config['MYSQL_DATABASE_DB'] = 'gamebox'
# app.config['MYSQL_DATABASE_HOST'] = 'localhost'
# app.config['CORS_HEADERS'] = 'Content-Type'

app.config['MYSQL_DATABASE_USER'] = 'Jw2Cm0qomm'
app.config['MYSQL_DATABASE_PASSWORD'] = 'zanN9Iqudf'
app.config['MYSQL_DATABASE_DB'] = 'Jw2Cm0qomm'
app.config['MYSQL_DATABASE_HOST'] = 'remotemysql.com'
app.config['CORS_HEADERS'] = 'Content-Type'

mysql.init_app(app)
