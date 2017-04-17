import smtplib
from getpass import getpass


class notificationbuddy(object):
    def __init__(self):
        self.server = smtplib.SMTP('smtp.gmail.com', 587)
        self.server.starttls()
        usr = prompt('Username: ')
        pss = getpass('Password: ')
        self.server.login(usr,pss)

    def send_email(self, msg):
        to_email = "cheualexander@gmail.com"
        from_email = "serverbudy@wiz.web"
        # msg = "A server went offline"
        self.server.sendmail(from_email, to_email, msg)

    def quit_server(self):
        self.server.quit()

def prompt(prompt):
    return raw_input(prompt).strip()
