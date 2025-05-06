import pymysql, os, bcrypt
from dotenv import load_dotenv

ERROR_1 = 'Wrong password.'
ERROR_2 = 'User does not exist.'

load_dotenv()

# create a connection to the database
def connection():
    return pymysql.connect(
        host = os.getenv('MYSQL_HOST'),
        user = os.getenv('MYSQL_USER'),
        password = os.getenv('MYSQL_PASSWORD'),
        database = os.getenv('MYSQL_DATABASE'),
    )

# create the main table
def create_db():
    with connection() as con:
        with con.cursor() as cur:
            # cur.execute('DROP TABLE users')
            # con.commit()
            cur.execute("CREATE TABLE IF NOT EXISTS users (id INT AUTO_INCREMENT PRIMARY KEY, username VARCHAR(255), password VARCHAR(255), rec_email VARCHAR(255))")

def user_already_registered(username: str) -> bool:
    with connection() as con:
        with con.cursor() as cur:
            cur.execute('SELECT * FROM users WHERE username = %s', (username, ))
            aaaaaa = cur.fetchone()
            if aaaaaa != None:
                return True
            else:
                return False
            
def check_password(password, hashed) -> bool:
    return bcrypt.checkpw(password.encode(), hashed.encode())

def get_password(username: str):
    with connection() as con:
        with con.cursor() as cur:
            cur.execute('SELECT password FROM users WHERE username = %s', (username, ))
            try:
                return cur.fetchone()[0]
            except TypeError:
                ...
            
def register_user(username: str, password: str) -> bool:
    with connection() as con:
        with con.cursor() as cur:
            cur.execute('INSERT INTO users (username, password) VALUES (%s, %s)', (username, password))
            con.commit()
            return True
        
def login_user(username: str, password: str) -> tuple[bool, str | None]:
    with connection() as con:
        with con.cursor() as cur:
            hashed_password = get_password(username)
            if bcrypt.checkpw(password.encode(), hashed_password.encode()):
                return True, None
            else:
                return False, ERROR_1
            
def reset_user_password(username: str, new_password: str) -> bool:
    with connection() as con:
        with con.cursor() as cur:
            cur.execute('UPDATE users SET password = %s WHERE username = %s', (new_password, username, ))
            con.commit()
            return True

def delete_user(username: str, password: str) -> bool:
    with connection() as con:
        with con.cursor() as cur:
            if user_already_registered(username):
                cur.execute('DELETE FROM users WHERE username = %s AND password = %s', (username, password, ))
                con.commit()
                return True
            else:
                return False

if __name__ == '__main__':
    print('wrong file executed.')