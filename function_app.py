import azure.functions as func
import logging
import msal
from OAuth2Service import getConfigInstance, getOAuth2Instance
import requests
from SendEmail.EmailSender import LucyTestEmailStrategy, EmailSender
app = func.FunctionApp(http_auth_level=func.AuthLevel.ANONYMOUS)

_configInstance = getConfigInstance()


tenant_id = _configInstance.get_tenant_id()
client_id = _configInstance.get_client_id()
client_secret = _configInstance.get_client_secret()
scopes = _configInstance.get_scopes()


authority = f'https://login.microsoft.com/{tenant_id}'
auth_app = msal.ConfidentialClientApplication(client_id,client_secret,authority)

redirect_send_email = _configInstance.get_send_email_redirect_uri()

def get_access_token(access_code,redirect_uri):
    token_response = auth_app.acquire_token_by_authorization_code(
        access_code, 
        scopes = scopes,
        redirect_uri = redirect_uri)
    
    if 'access_token' in token_response:
        return token_response['access_token']
    else:
        logging.info(token_response)
        raise Exception("Failed to receive access token")
    
@app.route(route="login_trigger")
def login_trigger(req: func.HttpRequest) -> func.HttpResponse:
    logging.info('Python HTTP trigger function processed a request.')
    auth_url = auth_app.get_authorization_request_url(scopes=scopes,
                                                 redirect_uri=redirect_send_email)
    
    logging.info(auth_url)
    # webbrowser.open(auth_url)
    # return func.HttpResponse(f'please login first')
    return func.HttpResponse(
        status_code=302,
        headers={'Location': auth_url}
    )


# Check response
    

@app.route(route="send_email", auth_level=func.AuthLevel.ANONYMOUS)
def send_email(req: func.HttpRequest) -> func.HttpResponse:
    auth_code = req.params.get("code")
    oauthInstance = getOAuth2Instance()

    if auth_code:
        try:
            access_token = get_access_token(auth_code,redirect_send_email)
            oauthInstance.setAccessToken(access_token)
            lucyTestStrategy = LucyTestEmailStrategy()
            sender = EmailSender(lucyTestStrategy)
            sender.send_email()
            return func.HttpResponse(f'email sent')
             
        except Exception as e:
            return func.HttpResponse(str(e))