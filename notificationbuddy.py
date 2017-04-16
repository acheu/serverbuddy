import smtplib
from getpass import getpass

def prompt(prompt):
    return raw_input(prompt).strip()

server = smtplib.SMTP('smtp.gmail.com', 587)
server.starttls()
usr = prompt('Username: ')
pss = getpass('Password: ')
server.login(usr,pss)

to_email = "cheualexander@gmail.com"
from_email = "serverbudy@wiz.web"
msg = "test email2"

server.sendmail(from_email, to_email, msg)

server.quit()
