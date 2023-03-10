import pymysql
import os
import web_socket_client
import asyncio
import getData
from datetime import datetime

# https://ming9mon.tistory.com/31 참조


class RonnyaDB:
    def __init__(self):
        self.log('DB Initialization started.')
        self.session = pymysql.connect(\
            host=os.getenv('db_host'),\
            user=os.getenv('db_user'),\
            password=os.getenv('db_password'),\
            charset='utf8')
        self.cur = self.session.cursor()

        self.cur.execute('SHOW DATABASES')
        databases = [x[0] for x in self.cur.fetchall()]
        if 'ronnya' not in databases:
            self.log('Database not found. Creating...',end='')
            self.cur.execute('CREATE DATABASE ronnya')
            print('Done')
        self.cur.execute('USE ronnya')

        self.cur.execute('SHOW TABLES')
        tables = [x[0] for x in self.cur.fetchall()]

        if 'user_info' not in tables:
            self.log('user_info information table not found. Creating... ', end='')
            self.cur.execute('\
                CREATE TABLE user_info (\
                    fid VARCHAR(20) PRIMARY KEY, \
                    uid BIGINT UNIQUE NOT NULL,\
                    name VARCHAR(20) NOT NULL,\
                    rank4 INT NOT NULL,\
                    point4 INT NOT NULL,\
                    rank3 INT NOT NULL,\
                    point3 INT NOT NULL,\
                    last_update DATETIME DEFAULT NOW()\
                )')
            print('Done')
        
        self.wsc = web_socket_client.WebSocketClient()
        self.cur = self.session.cursor(pymysql.cursors.DictCursor)
        self.log('DB Initialization done.')
    

    
    async def connect_wsc(self) -> bool:
        try:
            uid = os.getenv('ronnya_uid')
            token = os.getenv('ronnya_token')
            access_token = getData.GetToken(uid, token)['accessToken']
            version = getData.GetVersion()['version']
            version_str = 'web-' + '.'.join(version.split('.')[:-1])
            self.log('Initialize websocket connection')
            await self.wsc.connect()
            self.log('First heatbeat complete')

            self.log('Attempt to login')
            await self.wsc.login(access_token,uid,8,version,version_str)
            self.log('Initialize websocket connection Done')
            return True
        except Exception as e:
            print(type(e))
            print(e.args)
            print(e)
            return False    
        
    async def close(self):
        await self.wsc.close();
        self.session.close();
    
    async def get_info(self, fid: str) -> dict:
        '''
        Args
            fid: friend id of user
        
        Returns
            dict: information about user
        '''
        try:
            self.log('(FID: '+ fid + ') Checking existence in DB...')
            query = 'SELECT * FROM user_info WHERE fid = %s'
            self.cur.execute(query,(fid))
            result = self.cur.fetchall()

            if len(result) == 0:
                self.log('(FID: ' + fid + ') Not found. Sending request for data.')
                userdata=await self.wsc.find_user(fid)
                query='\
                    INSERT INTO\
                    user_info (fid,uid,name,rank4,point4,rank3,point3,last_update)\
                    VALUES (%s,%s,%s,%s,%s,%s,%s,%s)'
                nowdate=datetime.now()
                self.cur.execute(query,(fid,userdata['account_id'],userdata['nickname'],userdata['level']['id'],userdata['level']['score'],userdata['level3']['id'],userdata['level3']['score'],nowdate))
                self.session.commit()
                self.log('(FID: ' + fid + ') Added data to DB.')
                ret={
                    'fid' : fid,
                    'uid' : userdata['account_id'],
                    'name' : userdata['nickname'],
                    'rank4' : userdata['level']['id'],
                    'point4' : userdata['level']['score'],
                    'rank3' : userdata['level3']['id'],
                    'point3' : userdata['level3']['score'],
                    'last_update' : nowdate
                }
                return ret;
            
            else:
                self.log('(FID: ' + fid + ') Found. Checking update time...')
                diff=(datetime.now()-result[0]['last_update']).total_seconds()
                
                if diff <= 600: #업데이트한지 10분 미만일 경우 -> db 업데이트 안함
                    self.log('less 10 minutes have passed since last update.')
                    self.log('update aborted')
                    ret=result[0]
                    return ret
                
                else: #업데이트한지 10분 이상 지났을 경우 -> db 업데이트
                    self.log('over 10 minutes have passed since last update.')
                    self.log('update data...')
                    userdata=await self.wsc.find_user(fid)
                    query = '\
                        UPDATE user_info\
                        SET rank4=%s, point4=%s, rank3=%s, point3=%s, last_update=%s\
                        WHERE fid = %s'
                    nowdate=datetime.now()
                    self.cur.execute(query,(userdata['level']['id'],userdata['level']['score'],userdata['level3']['id'],userdata['level3']['score'],nowdate,fid))
                    self.session.commit()
                    userdata['level']['id'],userdata['level']['score'],userdata['level3']['id'],userdata['level3']['score']
                    ret={
                        'fid' : fid,
                        'uid' : userdata['account_id'],
                        'name' : userdata['nickname'],
                        'rank4' : userdata['level']['id'],
                        'point4' : userdata['level']['score'],
                        'rank3' : userdata['level3']['id'],
                        'point3' : userdata['level3']['score'],
                        'last_update' : nowdate
                    }
                    return ret

        except Exception as e:
            print(type(e))
            print(e.args)
            print(e)
            self.log('exception occured')
            return {}

    def log(self, msg: str, **print_options) -> None:
        print('[' + datetime.now().isoformat() + '] ' + msg, **print_options)

# For manual testing

async def main():
    print('----- Manual mode -----')
    r = RonnyaDB()
    await r.connect_wsc()
    commands = {
        'fetch': r.get_info
    }
    
    while True:
        print('>',end='')
        cmd = input().strip().split()
        if len(cmd) == 0:
            continue
        if cmd[0] == 'stop':
            break
        elif cmd[0] in commands.keys():
            status=await commands[cmd[0]](str(cmd[1]))
            print(f'\n\n{status}\n\n');
        else:
            print('No such command: ' + cmd[0])
            
    await r.close()

if __name__ == '__main__':
    asyncio.run(main())
