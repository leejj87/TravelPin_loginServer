from flask import Flask, jsonify, request,session
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
        return 'logged in'
    else:
        return 'email or password is not matched'

@app.route('/logout')
def logout():

    return 'logged out'
@app.route('/public_travel',methods=['GET'])
def view_all_travels():
    #closes from first
    #if specific city input
    #filter city -> type -> like most
    #default location is Los Angeles


    if city is not None:
        sql="""select * from {schema}.travel_plans where isPublic=1 and city='{city}'"""
    elif city is None:
        sql="""select * from {schema}.travel_plans where isPublic=1"""


if __name__ == "__main__":
    app.run()