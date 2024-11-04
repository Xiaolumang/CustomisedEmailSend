import re
from abc import ABC, abstractmethod
import requests
import json


from OAuth2Service import getOAuth2Instance



def get_match(s,field):
    match = re.search(f'<{field}>(.+)</{field}>',s, re.DOTALL)
    if match:
        return match.group(1)
    else:
        return ""

class Email:
    def __init__(self):
        self.subject = None
        self.body = None
        self.email_address = None

    def get_email_json(self):
        #print(self.body)
        email_data = {
        "message": {
        "subject": f'{self.subject}',
        "body": {
            "contentType": "HTML",
            "content": f"""
                {self.body}
                """
        },
        "toRecipients": [
            {
                "emailAddress": {
                    "address": f'{self.email_address}'
                }
            }
        ]
        
    },
    "saveToSentItems": "true"
}
        return email_data

class EmailBuilder:
    def __init__(self):
        self.email = Email()
    
    def set_subject(self, subject):
        self.email.subject = subject

    def set_body(self, body):
        self.email.body = body
    
    def set_email_address(self, email_address):
        self.email.email_address = email_address

    def build(self):
        return self.email
    
class EmailBody:
    def __init__(self):
        self.salutation = None
        self.meeting_time = None
        self.skeleton = None
        self.sender = None
        self.signature = None

    def get_email_body(self):
        
        self.skeleton = re.sub(r'\[salutation]',self.salutation,self.skeleton)
        
        self.skeleton = re.sub(r'\[meeting_time]',self.meeting_time,self.skeleton)
        
        self.skeleton = re.sub(r'\[sender]', self.sender,self.skeleton)
        self.skeleton = re.sub(r'\[signature]', self.signature,self.skeleton)
        
        
        return self.skeleton

        
class EmailBodyBuilder:
    def __init__(self):
        self.email_body = EmailBody()
    def set_salutation(self,salutation):
        self.email_body.salutation = salutation

    def set_meeting_time(self, meeting_time):
        self.email_body.meeting_time = meeting_time
    def set_skeleton(self, skeleton):
        self.email_body.skeleton = skeleton
    def set_sender(self,sender):
        self.email_body.sender = sender
    def set_signature(self,signature):
        self.email_body.signature = signature

    def build(self):
        return self.email_body


# def send_email(access_token, subject,body, email_address):
    


class EmailStrategy(ABC):
    @abstractmethod
    def generate_requirements(self):
        pass

class LucyTestEmailStrategy(EmailStrategy):
    def generate_requirements(self):
        template = dict()
        fields = ['subject','skeleton','recipients','meeting_time']
        with open('tmp', 'r') as f:
            s = f.read()
        for field in fields:
            template[field] = get_match(s,field)
        r = template['meeting_time'].split()
        name, time = r[::2], r[1::2]
        template['meeting_time'] = dict(zip(name, time))
        
        return template
        

# test = LucyTestEmailStrategy()
# x= test.generate_content()  
# print(x)  
def get_sender_name(access_token):
    response = requests.get(
    'https://graph.microsoft.com/v1.0/me',
    headers={'Authorization': f'Bearer {access_token}'}
)

# Check if the request was successful
    if response.status_code == 200:
        user_info = response.json()
        sender_email = user_info.get('mail') or user_info.get('userPrincipalName')
        sender =  re.search(r'.+(?=@)',sender_email).group(0).replace('.',' ').title()
        return sender
    else:
        print("Failed to get user info:", response.status_code, response.text)

class EmailSender:
    def __init__(self, strategy:EmailStrategy):
        self.strategy = strategy

    def set_strategy(self, strategy:EmailStrategy):
        self.strategy = strategy
    
    def send_email(self):
        requirements = self.strategy.generate_requirements()
        oauthInstance = getOAuth2Instance()
        access_token = oauthInstance.getAccessToken()

        email_body_builder = EmailBodyBuilder()
        

        sender = get_sender_name(access_token)

        for x in requirements['recipients'].split(";"):
            if x:
                email_body_builder.set_skeleton(requirements['skeleton'])
                email_address = re.search(r'<(.*)>',x).group(1)
                name = re.search(r'(\w+)\s\w+',x).group(1)
          
                salutation = f'Hi {name},'
                meeting_time = requirements['meeting_time']

                email_builder = EmailBuilder()
                email_builder.set_email_address(email_address)
                email_builder.set_subject(requirements['subject'])

                email_body_builder.set_salutation(salutation)
                email_body_builder.set_meeting_time(meeting_time[name])
                email_body_builder.set_sender(sender)
                sig = '<img style="display: block;-webkit-user-select: none;margin: auto;background-color: hsl(0, 0%, 90%);transition: background-color 300ms;" src="https://storage-thumbnails.bananatag.com/images/vQrfhZ/6e9ad3efae57a644802f91b36ed5bfbb.jpeg">'
                email_body_builder.set_signature(sig)

                email_builder.set_body(email_body_builder.build().get_email_body())
                email_data = email_builder.build().get_email_json()

                print(name, meeting_time[name]) 


                # Send the email using the Graph API
                response = requests.post(
                    url='https://graph.microsoft.com/v1.0/me/sendMail',
                    headers={
                        'Authorization': f'Bearer {access_token}',
                        'Content-Type': 'application/json'
                    },
                    json=email_data
                )
                if response.status_code == 202:
                    print("Email sent successfully with delegated permissions!")
                else:
                    print(f"Failed to send email: {response.status_code}, {response.text}")
            

                




# lucyTestStrategy = LucyTestEmailStrategy()
# sender = EmailSender(lucyTestStrategy)
# sender.send_email()