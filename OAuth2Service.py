import os
class OAuth2Service:
    def __init__(self):
        self.accessToken = None

    def getAccessToken(self):
        return self.accessToken
    
    def setAccessToken(self, at):
        self.accessToken = at

_oauth2Instance = None

def getOAuth2Instance():
    global _oauth2Instance
    if _oauth2Instance:
        return _oauth2Instance
    else:
        _oauth2Instance = OAuth2Service()
        return _oauth2Instance
    

class ConfigService:
    def __init__(self):
        self.tenant_id = os.getenv("TENANT_ID")
        self.client_id = os.getenv("CLIENT_ID")
        self.client_secret = os.getenv("CLIENT_SECRET")
        self.scopes = os.getenv("SCOPES").split(" ")
        self.send_email_redirect = os.getenv("REDIRECT_URI_EMAIL_TASK")

    def get_tenant_id(self):
        return self.tenant_id
    def get_client_id(self):
        return self.client_id
    def get_client_secret(self):
        return self.client_secret
    def get_scopes(self):
        return self.scopes
    def get_send_email_redirect_uri(self):
        return self.send_email_redirect

_configService = None

def getConfigInstance():
    global _configService
    if _configService:
        return _configService
    else:
        _configService = ConfigService()
        return _configService