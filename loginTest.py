import pymysql
from dotenv import load_dotenv
import os
import hashlib

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
with connection() as con:
    with con.cursor() as cur:
        cur.execute("CREATE TABLE IF NOT EXISTS users (id INT AUTO_INCREMENT PRIMARY KEY, username VARCHAR(255), password VARCHAR(255))")

# function that registers users
def register(username, password):
    with connection() as con:
        with con.cursor() as cur:
            cur.execute('SELECT * FROM users WHERE username = %s', (username,))
            # if / else that checks the existence of the user on the DB
            if cur.fetchone():
                print('User already registered')
                return False
            else:
                cur.execute('INSERT INTO users (username, password) VALUES (%s, %s)', (username, password))
                print('User registered successfully')
                con.commit()

# function that logs in users
def login(username, password):
    with connection() as con:
        with con.cursor() as cur:
            cur.execute('SELECT * FROM users WHERE username = %s AND password = %s', (username, password))
            # if / else that checks the existence of the user on the DB
            if cur.fetchone():
                print('Login successful')
                return True
            else:
                print('Invalid credentials')
                return False

def main():
    choice = input('Do you want to:\n1. Register\n2. Login\n')
    if choice == '1':
        username = input('Enter email: ')
        password = input('Enter password: ')
        # Hash the password before calling the login function
        enc_password = hashlib.sha256(password.encode()).hexdigest()
        register(username, enc_password)

    elif choice == '2':
        username = input('Enter email: ')
        password = input('Enter password: ')
        # Hash the password before calling the login function
        enc_password = hashlib.sha256(password.encode()).hexdigest()
        login(username, enc_password)
    else:
        print('Invalid choice')
        return

if __name__ == '__main__':
    main()