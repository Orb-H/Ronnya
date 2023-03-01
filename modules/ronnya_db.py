import pymysql
import datetime as dt
import os
import web_socket_client

# https://ming9mon.tistory.com/31 참조

class RonnyaDB:
    def __init__(self):
        self.log('Initialization started.')
        self.session = pymysql.connect(host=os.getenv('db_host'), user=os.getenv('db_user'), password=os.getenv('db_password'), charset='utf8')
        self.cur = self.session.cursor()

        self.wsc = web_socket_client.WebSocketClient()

        self.cur.execute('SHOW DATABASES')
        databases = [x[0] for x in self.cur.fetchall()]
        if 'ronnya' not in databases:
            self.log('Database not found. Creating...')
            self.cur.execute('CREATE DATABASE ronnya')
            print('Done')
        self.cur.execute('USE ronnya')

        self.cur.execute('SHOW TABLES')
        tables = [x[0] for x in self.cur.fetchall()]

        if 'uid_info' not in tables:
            self.log('User ID information table not found. Creating... ', end='')
            self.cur.execute('CREATE TABLE uid_info (fid VARCHAR(20) PRIMARY KEY, uid BIGINT UNIQUE NOT NULL)')
            print('Done')
        if 'rank_info' not in tables:
            self.log('Rank information table not found. Creating... ', end='')
            self.cur.execute('CREATE TABLE rank_info (fid VARCHAR(20) PRIMARY KEY, name VARCHAR(20) NOT NULL, rank4 INT NOT NULL, point4 INT NOT NULL, rank3 INT NOT NULL, point3 INT NOT NULL, last_update DATETIME DEFAULT NOW())')
            print('Done')
        
        self.log('Initialization done.')
    
    def get_info(self, fid: str) -> dict:
        '''
        Args
            fid: friend id of user
        
        Returns
            dict: information about user
        '''
        self.log('(FID: '+ fid + ') Checking existence in DB...')
        query = 'SELECT * FROM uid_table WHERE fid = ' + fid
        self.cur.execute(query)
        result = self.cur.fetchall()

        if len(result) == 0:
            self.log('(FID: ' + fid + ') Not found. Sending request for data.')
            ### calling websocket to get data ###
            ### Return value: uid, name, rank4, point4, rank3, point3 ###
            # query = 'INSERT INTO uid_table VALUES (' + fid + ',' + uid  + ')'
            # self.cur.execute(query)
            self.log('(FID: ' + fid + ') Added data to DB.')
        else:
            self.log('(FID: ' + fid + ') Found. Checking update time...')
            
            # query = 'SELECT * FROM rank_tables where fud = ' + fid
            # self.cur.execute(query)
            # result = self.cur.fetchall()
            
            # query = 'UPDATE rank_tables SET ... WHERE fid = ' + fid
            # self.cur.execute(query)

    def log(self, msg: str, **print_options) -> None:
        print('[' + dt.datetime.now().isoformat() + '] ' + msg, **print_options)

# For manual testing
if __name__ == '__main__':
    print('----- Manual mode -----')
    r = RonnyaDB()
    commands = {
        'fetch': r.get_info
    }
    while True:
        cmd = input().strip().split()
        if len(cmd) == 0:
            continue
        if cmd[0] == 'stop':
            break
        elif cmd[0] in commands.keys():
            commands[cmd[0]][cmd[1:]]
        else:
            print('No such command: ' + cmd[0])