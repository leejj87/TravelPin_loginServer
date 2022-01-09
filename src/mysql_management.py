import mysql.connector
import pandas as pd
import datetime
class Connection(object):
    """mysql Connection class
        instance: host,user,password
        query set up -- > setQuery
        select statement --> select_statement"""
    def __init__(self,host,user,password,port=3306):
        self.connection_info=None
        self.host=host
        self.user=user
        self.__password=password
        self.port=port
        self.mydb=None
    @property
    def getHost(self):
        return self.host
    @property
    def getUser(self):
        return self.user
    def connection(self):
        self.mydb = mysql.connector.connect(host=self.host, port=self.port, user=self.user, password=self.__password,charset="utf8")
        return self.mydb

    def close_cursor(self,cursor):
        try:
            cursor.close()
        except Exception as err:
            print(err)
    def close_connection(self):
        if self.mydb is not None:
            try:
                self.mydb.close()
            except Exception as err:
                print(err)

    # def updateDataFrame(self,updated_dataFrame,table_name,schema):
    #     engine = create_engine("mysql://{username}:{password}@{host}".format(username=self.getUser,password=self.__password,host=self.getHost))
    #     con = engine.connect()
    #     df = updated_dataFrame
    #     df.to_sql(name=table_name, con=con, if_exists='replace')
    #     con.close()
    #     #updated_dataFrame.to_sql(name=table_name,con=self.mydb,if_exists='replace')
class QueryManager(Connection):
    def __init__(self,host,user,password,port):
        super().__init__(host, user, password, port)
        self.connection()
    @property
    def getQuery(self):
        return self.sql_query
    @getQuery.setter
    def setQuery(self, query):
        self.sql_query = query
    def select_statement(self):
        """:return generator"""
        if self.getQuery is not None:
            mycursor = self.mydb.cursor()
            mycursor.execute(self.getQuery)
            while True:

                myresult = mycursor.fetchone()
                if myresult is None:
                    break
                yield myresult
    def sql_to_pandas(self):
        """:return dataframe """
        df = pd.read_sql(self.getQuery, self.mydb)
        return df
    def executeQuery(self):
        if self.sql_query is not None:
            try:
                self.cursor = self.mydb.cursor()
                sql = self.getQuery
                self.cursor.execute(sql)
            except Exception as err:
                print(err)
                print(sql)
                self.mydb.rollback()
                raise Exception(str(err))
            else:
                self.mydb.commit()
    def close(self):
        try:
            self.close_cursor(self.cursor)
        except:
            pass
        finally:
            self.close_connection()
class MysqlQue(object):
    def __init__(self):
        self.__dict_que={}
    def __getitem__(self, item):
        return self.__dict_que.get(item)
    def __setitem__(self, key, value):
        self.__dict_que[key]=value
    def __len__(self):
        return len(self.__dict_que)
    def que_generator(self,key,instance,expiredDate):
        self[key]={}
        self[key]['instance']=instance
        self[key]['expiredDate']=expiredDate
    def isValid(self,key):
        return key in self.__dict_que
    def que_terminate(self,key):
        if self.isValid(key):
            instance=self[key]['instance']
            instance.close()
            del self.__dict_que[key]
        return True
    def garbageCollector(self):
        key_collector=[]
        for key,sub_dict in self.__dict_que.items():
            if datetime.datetime.now()>=sub_dict['expiredDate']:
                key_collector.append(key)
        return key_collector
    def autoTerminate(self):
        for i in self.garbageCollector():
            self.que_terminate(i)

if __name__ == '__main__':
    instance1=QueryManager('server.echoad.co.kr','jlee','dlwhdwls12',33069)
    instance2 = QueryManager('server.echoad.co.kr', 'jlee', 'dlwhdwls12', 33069)
    instance3=QueryManager('server.echoad.co.kr','jlee','dlwhdwls12',33069)
    query="""select * from general_schema.member"""
    instance1.setQuery=query
    df=instance1.sql_to_pandas()
    print(df)
    instance_que=MysqlQue()
    instance_que.que_generator('instance1',instance1,datetime.datetime.strptime('12-25-2021 11:00:00',"%m-%d-%Y %H:%M:%S"))
    leng=len(instance_que)
    print(leng)
    how=instance_que.garbageCollector()
    print(how)
    new_instance1=instance_que['instance1']['instance']
    print(new_instance1)