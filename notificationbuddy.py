import smtplib
from getpass import getpass


class notificationbuddy(object):
    def __init__(self):
        check = prompt('Log into email? (Y/N): ')
        if check.upper() == 'Y':
            self.server = smtplib.SMTP('smtp.gmail.com', 587)
            self.server.starttls()
            self.usr = prompt('Username: ')
            pss = getpass('Password: ')
            try:
                self.server.login(self.usr,pss)
            except:
                print 'Username and Password Not Accepted'
        else:
            self.server = 0

    def send_email(self, msg):
        if self.server != 0:
            to_email = self.usr + '@gmail.com'
            from_email = "mona@wiz.web"
            self.server.sendmail(from_email, to_email, msg)

    def quit_server(self):
        if self.server > 0:
            self.server.quit()

def prompt(prompt):
    return raw_input(prompt).strip()
