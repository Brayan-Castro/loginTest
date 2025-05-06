import re, bcrypt
import modules.db_manager as db
from modules.email_manager import email_verification as email

ERROR_1 = 'User already exists.'
ERROR_2 = 'User does not exist.'
ERROR_3 = 'Invalid choice.'
ERROR_4 = 'Passwords dont match.'

def hash_password(password: str) -> str:
    salt = bcrypt.gensalt()
    password = bcrypt.hashpw(password.encode(), salt)
    return password

def register(username: str, password: str) -> tuple[bool, str | None]:
    if db.user_already_registered(username):
        return False, ERROR_1
    else:
        success, error = email(username)
        if success:
            if db.register_user(username, password):
                    return True, None
        else:
            return False, error
                    
def login(username: str, password: str) -> tuple[bool, str | None]:
    if db.user_already_registered(username):
        success, error = db.login_user(username, password)
        if success:
            success, error = email(username)
            if success:
                return True, None
            else:
                return False, error
        else:
            return False, error
    else:
        return False, ERROR_2

def reset_password(username: str) -> tuple[bool, str | None]:
    success, error = email(username)
    if success:
        password = input('Enter the new password: ')
        hashed_password = hash_password(password)
        db.reset_user_password(username, hashed_password)
        return True, None
    else:
        return False, error

def delete_user(username: str, password: str) -> tuple[bool, str | None]:
    success, error = email(username)
    if success:
        if db.delete_user(username, password):
            return True, None
        else:
            return False, ERROR_3
    else:
        return False, error

def main():
    db.create_db()
    choice = input('Do you want to:\n1. Register\n2. Login\n3. Delete User\n')
    match(choice):
        case '1': # Register
            username = input('Enter email: ')
            if not re.match(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$', username):
                print('Invalid Email.')
                return

            password = input('Enter password: ')
            password_ver = input('Confirm password: ')

            if password_ver == password:
                hashed_password = hash_password(password)
                success, error = register(username, hashed_password)
                if success:
                    print('User Registered Successfully.')
                else:
                    print(error)
            else:
                print(ERROR_4)
        case '2': # Log-in
            username = input('Enter email: ')
            password = input('Enter password: ')

            success, error = login(username, password)

            if success:
                print('User Logged in successfully.')
            elif error == 'Wrong Password.':
                print(error)
                secure_auth = input('Do you want to reset your password? (y/n) ')
                if secure_auth.lower() == 'y':
                    success, error = reset_password(username)
                    if success:
                        print('Password changed sucessfully.')
                    else:
                        print(error)
            else:
                print(error)
        case '3': # Delete user
                username = input('Enter email: ')
                password = input('Enter password: ')

                password = hash_password(password)

                success, error = delete_user(username, hashed_password)
                if success:
                    print('User deleted successfully.')
                else:
                    print(error)
        case _:
            print(ERROR_3)
            return

if __name__ == '__main__':
    main()