import smtplib, os, secrets
from email.message import EmailMessage
from dotenv import load_dotenv

load_dotenv()

ERROR_1 = 'Invalid Code.'

def send_email(receiver: str, code: int) -> tuple[bool, str | None]:
    sender_email = os.getenv('SENDER_EMAIL')
    sender_pw = os.getenv('SENDER_PW')

    msg = EmailMessage()
    msg['Subject'] = 'Two-Factor Authentication'
    msg['From'] = sender_email
    msg['To'] = receiver
    msg.set_content(f'Verificaton Code: {code}')

    try:
        with smtplib.SMTP('smtp.gmail.com', 587) as smtp:
            smtp.starttls()
            smtp.login(sender_email, sender_pw)
            smtp.send_message(msg)
            return True, None
    except Exception as error:
        return False, str(error)
    
def email_verification(username: str) -> tuple[bool, str | None]:
    code = 10000 + secrets.randbelow(99999 - 10000 + 1)
    success, error = send_email(username, code)
    if success:
        code_ver = int(input('Enter the verification code sent to email: '))
        if code_ver == code:
            return True, None
        else:
            return False, ERROR_1
    else:
        return False, error
    
if __name__ == '__main__':
    print('wrong file executed.')