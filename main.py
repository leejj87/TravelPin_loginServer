from flask import Flask, jsonify, request,session,redirect
import os
#from src.util import encryped
import uuid
from src import util
from src import ini_path
from src.mysql_management import QueryManager,MysqlQue
ini_settings=util.jsonFileToDict(ini_path)
app = Flask(__name__)
app.secret_key = ini_settings['SECRET_KEY']
SQLSESSION=MysqlQue()
@app.route('/')
def index():
    if 'email' in session:
        return session['email']
    else:
        return redirect('/login')
@app.route('/sign-up', methods = ['POST'])
def sign_up():
    try:
        user = request.get_json()
        user['password']=util.encryped(user['password'])
        #password=user['password']
        sql_user=ini_settings.get('db').get('user')
        sql_password=ini_settings.get('db').get('password')
        sql_host=ini_settings.get('db').get('host')
        sql_port=ini_settings.get('db').get('port')
        sql_instance=QueryManager(sql_host,sql_user,sql_password,sql_port)
        sql="""INSERT INTO {schema}.member (
                                email,UserNickName,
                                password
                               ) VALUES (
                                '{email}',
                                '{nickname}',
                                '{password}'
                               )""".format(schema=ini_settings['db']['database'],email=user['email'],
                                           nickname=user['name'],password=user['password'])
        sql_instance.setQuery=sql
        sql_instance.executeQuery()
        sql_instance.close()
    except Exception as err:
        return str(err),404
    return "New User Added", 200
@app.route('/login', methods=['POST'])
def login():
    user = request.get_json()
    user['password'] = util.encryped(user['password'])
    sql_user = ini_settings.get('db').get('user')
    sql_password = ini_settings.get('db').get('password')
    sql_host = ini_settings.get('db').get('host')
    sql_port = ini_settings.get('db').get('port')
    sql_instance = QueryManager(sql_host, sql_user, sql_password, sql_port)
    sql="""select * from {schema}.member where email='{email}' and password='{password}'""".format(schema=ini_settings['db']['database'],
                                                                        email=user['email'],password=user['password'])
    sql_instance.setQuery=sql
    df=sql_instance.sql_to_pandas()
    sql_instance.close()
    if not df.empty:
        session['email']=user['email']
        return 'logged in'
    else:
        return 'email or password is not matched'
@app.route('/logout')
def logout():
    session.pop("email",None)
    return 'logged out'

#my trips
@app.route('/my_saves',methods=['POST'])
def my_saves():
    pass

#public use functions
@app.route('/public_travel',methods=['GET'])
def view_all_travels():
    getters=request.args.to_dict()
    try:
        lat=float(getters['lat'])
        lng=float(getters['long'])
        radius=float(getters['radius'])
    except:
        #default is at Los Angeles
        lat,lng,radius=33.973093,-118.247896,50
    sql_user = ini_settings.get('db_public_select').get('user')
    sql_password = ini_settings.get('db_public_select').get('password')
    sql_host = ini_settings.get('db_public_select').get('host')
    sql_port = ini_settings.get('db_public_select').get('port')
    sql_instance = QueryManager(sql_host, sql_user, sql_password, sql_port)
    sql="""SELECT id,member_id,city_code,travel_concept,likes,hash_tags 
    FROM {schema}.travel_plans WHERE isPublic =1 AND id IN(
    SELECT travel_id FROM {schema}.travel_plans_details_geodata_average WHERE 69.0 *DEGREES(ACOS(LEAST(1.0, COS(RADIANS(lat))
         * COS(RADIANS({lat}))
         * COS(RADIANS(lng - ({lng})))
         + SIN(RADIANS(lat))
         * SIN(RADIANS({lat}))))) <={radius}) order by likes desc""".format(schema=ini_settings['db']['database'],
                                                                            lat=lat,lng=lng,radius=radius)
    sql_instance.setQuery=sql
    df=sql_instance.sql_to_pandas()
    result_json=df.to_json(orient = 'records')
    return result_json


if __name__ == "__main__":
    app.run()