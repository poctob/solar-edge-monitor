import sendgrid
from sendgrid.helpers.mail import *

class EmailManager:

    def sendAlertEmail(self, api_key, to, from_email, serial):
        sg = sendgrid.SendGridAPIClient(api_key=api_key)
        from_email = Email(from_email)
        to_email = To(to)
        subject = "SolarEdge Alert"
        content = Content("text/plain", f'''Your solar edge power generation is outside of acceptable parameters. 
        Please login into SolarEdge portal and review generation data.
        This alert was generated for the inverter with serial number {serial}''')
        mail = Mail(from_email, to_email, subject, content)
        response = sg.send(mail) 
        return response
