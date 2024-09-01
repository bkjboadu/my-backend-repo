import secrets

def generate_activation_token():
    return secrets.token_urlsafe(32)