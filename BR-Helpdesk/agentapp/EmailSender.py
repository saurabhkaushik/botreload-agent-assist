import smtplib

class EmailSender(object):
    def send(self):
        print ('Email Sending Module : ')
        gmail_user = 'botreload@gmail.com'  
        gmail_password = 'Imsk1990@'

        sent_from = gmail_user  
        to = ['saurabhk666@gmail.com']  
        subject = 'OMG Super Important Message'  
        body = 'Hey, what\'s up?\n\n- You'

        email_text = str("""\  
            From: %s  
            To: %s  
            Subject: %s
            %s
            """ % (sent_from, ", ".join(to), subject, body))
        #try:  
        print ('sfds')
        server = smtplib.SMTP_SSL('smtp.gmail.com:465')
        print ('fsdfd')
        server.ehlo()
        print ('before2')
        #server.ehlo()
        server.starttls()
        print ('before')
        server.login(gmail_user, gmail_password)
        print ('loing')
        server.sendmail(sent_from, to, email_text)
        server.close()
        print ('Email sent!')
        #except:  
        #     print ('Something went wrong...')