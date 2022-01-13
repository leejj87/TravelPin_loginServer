from flask import Flask, jsonify, request,session,redirect
import hashlib
import config
import os
#from src.util import encryped

from src import util
from src import ini_path
from src.mysql_management import QueryManager,MysqlQue
ini_settings=util.jsonFileToDict(ini_path)
app = Flask(__name__)
app.secret_key = ini_settings['SECRET_KEY']
SQLSESSION=MysqlQue()
@app.route('/')
def index():
    return "Developing Page"
@app.route('/sign-up', methods = ['POST'])
def sign_up():
    try:
        user = request.get_json()
        user['password']=util.encryped(user['password'])
        #password=user['password']
        db_access=config.DB_settings().getAccess('db')
        if db_access is None: raise Exception("DB ACCESS FAILS")
        sql_instance=QueryManager(db_access['host'],db_access['user'],db_access['password'],db_access['port'])
        key_string=user['email']+ini_settings.get("DB_PASSWORD_KEY")
        private_key= hashlib.sha256(key_string.encode())
        private_key=private_key.hexdigest()
        sql="""INSERT INTO {schema}.member (
                                email,UserNickName,
                                password,privateKey
                               ) VALUES (
                                '{email}',
                                '{nickname}',
                                '{password}',
                                '{private_key}'
                               )""".format(schema=ini_settings['db']['database'],email=user['email'],
                                           nickname=user['name'],password=user['password'],private_key=private_key)
        sql_instance.setQuery=sql
        sql_instance.executeQuery()
        sql_instance.close()
    except Exception as err:
        return "false",str(err)
    return "true"
@app.route('/login', methods=['POST'])
def login():
    user = request.get_json()
    user['password'] = util.encryped(user['password'])
    db_access = config.DB_settings().getAccess('db')
    if db_access is None: raise Exception("DB ACCESS FAILS")
    sql_instance = QueryManager(db_access['host'], db_access['user'], db_access['password'], db_access['port'])
    sql="""select * from {schema}.member where email='{email}' and password='{password}'""".format(schema=ini_settings['db']['database'],
                                                                        email=user['email'],password=user['password'])
    sql_instance.setQuery=sql
    df=sql_instance.sql_to_pandas()
    sql_instance.close()
    if not df.empty:
        session['email']=user['email']
        private_key=df['privateKey'][0]
        return private_key
    else:
        return "null"
@app.route('/logout')
def logout():
    session.pop("email",None)
    return 'logged out'

#my trips
@app.route('/my_saves',methods=['POST'])
def my_saves():
    try:
        user = request.get_json()
        # verify process
        private_key=user['private_key']
        require=config.PrivateKeyVerification(private_key)
        log_in_verified=require.verification()
        # verify process done
        if log_in_verified is not None:
            member_id=log_in_verified
            sql = """select * from {schema}.travel_plans where member_id = {mem_id} order by modified_date desc""".format(
                schema=ini_settings['db']['database'],mem_id=member_id)
            db_access = config.DB_settings().getAccess('db')
            if db_access is None: raise Exception("DB ACCESS FAILS")
            sql_instance = QueryManager(db_access['host'], db_access['user'], db_access['password'], db_access['port'])
            sql_instance.setQuery=sql
            df_travel = sql_instance.sql_to_pandas()
            sql_instance.close()
            if df_travel.empty:return jsonify([])
            result_json = df_travel.to_json(orient='records')
            return result_json
        else:
            return "false","valid private key required"
    except Exception as err:
        return "false",str(err)
#setUp trips
#insert new trip
@app.route('/new-trip',methods=['POST'])
def addNewTrip():
    try:
        user = request.get_json()
        # verify process
        private_key = user['private_key']
        city=user['city']
        state=user['state']
        concept=user['concept']
        isPublic=user['is_public']
        require = config.PrivateKeyVerification(private_key)
        log_in_verified = require.verification()
        # verify process done
        if log_in_verified is not None:
            mem_id=log_in_verified
            city_code=config.city_finder(city,state)
            if city_code is None: return "null","city code error"
            sql="""insert into {schema}.travel_plans (member_id,city_code,travel_concept,isPublic)
            values ({mem_id},{city_code},'{concept}',{is_public})""".format(mem_id=mem_id,city_code=city_code,
                                                                            concept=concept,isPublic=isPublic)
            db_access = config.DB_settings().getAccess('db')
            if db_access is None: raise Exception("DB ACCESS FAILS")
            sql_instance = QueryManager(db_access['host'], db_access['user'], db_access['password'], db_access['port'])
            sql_instance.setQuery = sql
            sql_instance.executeQuery()
            sql_instance.close()
    except Exception as err:
        return "false",str(err)
    else:
        return "true"
#update trip
@app.route('/trip-update',methods=['POST'])
def updateNewTrip():
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
    db_access = config.DB_settings().getAccess('db_public_select')
    if db_access is None: raise Exception("DB ACCESS FAILS")
    sql_instance = QueryManager(db_access['host'], db_access['user'], db_access['password'], db_access['port'])
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
    sql_instance.close()
    result_json=df.to_json(orient = 'records')
    return result_json

@app.route('/locations')
def view_all_locations():
    db_access = config.DB_settings().getAccess('db_public_select')
    if db_access is None: raise Exception("DB ACCESS FAILS")
    sql_instance = QueryManager(db_access['host'], db_access['user'], db_access['password'], db_access['port'])
    sql ="""select * from {}.RegionGeoInfo""".format(ini_settings['db']['database'])
    sql_instance.setQuery=sql
    df=sql_instance.sql_to_pandas()
    return df.to_json(orient = 'records')

if __name__ == "__main__":
    app.run()