import pymysql
from dotenv import load_dotenv
import os
import hashlib
import smtplib
from email.message import EmailMessage
from random import randrange
import re

# There are variables with the same name that are used on different functions of this program, but they keep consistent what value they hold.
# code: holds the value of the code sent to email as 2FA
# code_ver: holds the value of the code inputted by the user on the terminal
# recovery_email: holds the recovery email
# username
# password
# password: encrypted password
# email_result: hold the returning value of the send_email function

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
        # cur.execute('DROP TABLE users')
        # con.commit()
        cur.execute("CREATE TABLE IF NOT EXISTS users (id INT AUTO_INCREMENT PRIMARY KEY, username VARCHAR(255), password VARCHAR(255), rec_email VARCHAR(255))")

# function that sends the user verification emails, uses smtplib and gmail.
def send_email(receiver, code):
    sender_email = os.getenv('SENDER_EMAIL')
    sender_pw = os.getenv('SENDER_PW')

    msg = EmailMessage()
    msg['Subject'] = 'Two-Factor Authentication'
    msg['From'] = sender_email
    msg['To'] = receiver
    msg.set_content(f'Verificaton Code: {code}')

# Tries to send the email through gmail.
    try:
        with smtplib.SMTP('smtp.gmail.com', 587) as smtp:
            smtp.starttls()
            smtp.login(sender_email, sender_pw)
            smtp.send_message(msg)
            return 'Success'
    except Exception as error:
        return error

# function that registers users
def register(username, password):
    # Generates a random number between 1000 / 9999 to be used as verification.
    code = randrange(1000, 9999)
    with connection() as con:
        with con.cursor() as cur:
            # Sends the code to the user through email.
            email_result = send_email(username, code)
            if email_result == 'Success':
                # Checks if the user typed in the right code.
                code_ver = int(input('Enter the verification code sent to email: '))
                if code_ver == code:
                    # Checks if the user already exists.
                    cur.execute('SELECT * FROM users WHERE username = %s', (username, ))
                    if cur.fetchone():
                        return 'User Already Exists.'
                    else:
                        cur.execute('INSERT INTO users (username, password) VALUES (%s, %s)', (username, password))
                        con.commit()
                        return 'User Registered Successfully.'
                else:
                    return 'Invalid Code.'
            # Prints out the error that send_email returned.
            else:
                print('Failed to send email verification code.')
                return email_result

# function that logs in users
def login(username, password):
    with connection() as con:
        with con.cursor() as cur:
            # Generates a random number between 1000 / 9999 to be used as verification.
            code = randrange(1000, 9999)
            # Checks if the user exists.
            cur.execute('SELECT * FROM users WHERE username = %s', (username, ))
            if cur.fetchone():
                # Checks if the user typed the right password.
                cur.execute('SELECT * FROM users WHERE username = %s AND password = %s', (username, password))
                if cur.fetchone():
                    # Sends the code to the user through email.
                    email_result = send_email(username, code)
                    if email_result == 'Success':
                        # Checks if the user typed in the right code.
                        code_ver = int(input('Enter the verification code sent to email: '))
                        if code_ver == code:
                            # Checks if the user has a recovery email in the account.
                            if not check_recovery(username):
                                return 'log no rec'
                            return 'Log rec'
                        else:
                            return 'Invalid Code.'
                    # Prints the error that send_email returned
                    else:
                        print('Failed to send email verification code.')
                        print(email_result)
                else:
                    return 'Invalid Password.'

# function that resets a user password.
def reset_password(username, new_password):
    with connection() as con:
        with con.cursor() as cur:
            # Generates a random number between 1000 / 9999 to be used as verification
            code = randrange(1000, 9999)
            # Sends the code to the user through email.
            email_result = send_email(username, code)
            if email_result == 'Success':
                # Checks if the user typed in the right code.
                code_ver = int(input('Enter the verification code sent to email: '))
                if code_ver == code:
                    cur.execute('SELECT * FROM users WHERE username = %s OR rec_email = %s', (username, username, ))
                    # Updates the user email based on the account username or account recovery email
                    if cur.fetchone():
                        cur.execute('UPDATE users SET password = %s WHERE username = %s OR rec_email = %s', (new_password, username, username, ))
                        con.commit()
                        return 'Password changed successfully.'
                else:
                    return 'Invalid Code, please try again.'
            else:
                print('Failed to send email verification code.')
                return email_result

# functions that add a recovery email to an account.
def add_rec_email(username, rec_email):
    # Generates a random number between 1000 / 9999 to be used as verification
    code = randrange(1000, 9999)
    # Sends the code to the user through email.
    email_result = send_email(rec_email, code)
    if email_result == 'Success':
        # Checks if the user typed in the right code.
        code_ver = int(input('Enter the verification code sent to email: '))
        if code_ver == code:
            with connection() as con:
                with con.cursor() as cur:
                    # Adds a recovery email to the account.
                    cur.execute('UPDATE users SET rec_email = %s WHERE username = %s', (rec_email, username))
                    con.commit()
                    return 'Recovery email added Successfully.'
        else:
            return 'Invalid Code'
    else:
        print('Failed to send email verification code.')
        return email_result

# function that checks if there is already a recovery email in the account.
def check_recovery(username):
    with connection() as con:
        with con.cursor() as cur:
            cur.execute('SELECT rec_email FROM users WHERE username = %s', (username,))
            recovery_email = cur.fetchone()
            # fetchone() returns a tuple with only None inside it, so if the value is different than that we return the email, otherwise return false (it makes error handling easier).
            if recovery_email != (None, ):
                return recovery_email
            else:
                return False

# function that deletes an user.
def delete_user(username, password):
    with connection() as con:
        with con.cursor() as cur:
            # Generates a random number between 1000 / 9999 to be used as verification
            code = randrange(1000, 9999)
            # Sends the code to the user through email.
            email_result = send_email(username, code)
            if email_result == 'Success':
                    # Checks if the user typed in the right code.
                    code_ver = int(input('Enter the verification code sent to email: '))
                    if code_ver == code:
                        cur.execute('DELETE FROM users WHERE username = %s AND password = %s', (username, password, ))
                        con.commit()
                        return True
                    else:
                        print('Could not Delete User.')
                        return False
            else:
                print(email_result)

def main():
    choice = input('Do you want to:\n1. Register\n2. Login\n3. Delete User\n')
    match(choice):
        case '1': # Register
            username = input('Enter email: ')
            # Checks if the user email is in the right format.
            if not re.match(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$', username):
                print('Invalid Email.')
            password = input('Enter password: ')

            # Encrypts the password before calling the login function.
            password = hashlib.sha256(password.encode()).hexdigest()

            # Calls the register function with the email and hashed password.
            register(username, password)

            # Adds a recovery email to the account if the users wants it.
            secure_auth = input('There is no recovery email in the account, do you want to add one (y/n): ')
            if secure_auth.lower() == 'y':
                rec_email = input('Enter the email you want to use as recovery: ')
                # Checks if the user email is in the right format and if its the same as the main email.
                if (not re.match(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$', rec_email)) or rec_email == username:
                    print('Invalid Email.')
                else: 
                    print(add_rec_email(username, rec_email))
            else:
                ...

        case '2': # Log-in
            username = input('Enter email: ')
            password = input('Enter password: ')

            # Hash the password before calling the login function
            password = hashlib.sha256(password.encode()).hexdigest()
            login_result = login(username, password)

            # Checks the return value of login (makes error handling easier).
            match(login_result):
                # if the user logged in successfully but has no recovery email in the account this happens.
                case 'log no rec':
                    print('Login Successfull.')
                    secure_auth = input('Logged in Successfully but theres no recovery email in the account, do you want to add one (y/n): ')
                    if secure_auth.lower() == 'y':
                        rec_email = input('Enter the recovery email: ')
                        if add_rec_email(username, rec_email):
                            print('Recovery email added successfully.')
                        else:
                            print('Failed to add recovery email.')
                
                # if the user logged in successfully and already have a recovery email in the account this happens.
                case 'Log rec':
                    print('Login Successfull.')

                # if the user typed the wrong verification code this happens.
                case 'Invalid Code.':
                    print('Invalid Code, please try again.')

                # if the user typed the wrong password code this happens.
                case 'Invalid Password.':
                    secure_auth = input('Invalid Password, do you want to reset it? (y/n) ')
                    if secure_auth.lower() == 'y':
                        # Asks for and encrypts the new password.
                        new_password = input('Enter the new password: ')
                        new_password = hashlib.sha256(new_password.encode()).hexdigest()
                        # Checks if the user has a recovery email in the account (recovery emails have this single purpose, as 2fa is done ny the main email).
                        rec_email = check_recovery(username)
                        # Calls the rec_mail function with or without the recovery email depending on its existence.
                        # (yes the recovery email is basically useless, but, if the user has no rec_email in the account, the function will probably break).
                        if rec_email:
                            print(reset_password(rec_email, new_password))
                        else:
                            print(reset_password(username, new_password))

                # If the 1st search query returned nothing (therefore there is no user with that email) this happens.
                case _:
                    print('User not found')

        case '3': # Delete user
                username = input('Enter email: ')
                password = input('Enter password: ')
                password = hashlib.sha256(password.encode()).hexdigest()

                delete_user_result = delete_user(username, password)

                # prints the result of the delete_user function.
                if delete_user_result:
                    print('User Deleted Successfully')
                else:
                    print('Failed to Delete user')

        case _:
            print('Invalid choice')
            return

if __name__ == '__main__':
    main()