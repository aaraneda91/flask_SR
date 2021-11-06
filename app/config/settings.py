class Connection():
   USER = 'postgres'
   PASSWORD = 'admin'
   SERVER = 'localhost'
   PORT = '5433'
   DB_NAME = 'sistema_respaldos'
   SECRET_KEY= 'ATCVDWEXGZH2J4M5N6Q8R9SBUCVDXFYGZJ3K4M6P7Q8SATBUCWEXFYH2J3'
   SQLALCHEMY_DATABASE_URI = 'postgresql://'+USER+':'+PASSWORD+'@'+SERVER+':'+PORT+'/'+DB_NAME