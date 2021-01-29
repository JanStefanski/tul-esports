from os import environ

class ConfigLoader:

    def __init__(self, app):
        print("Loading Config...")
        app.config['SECRET_KEY'] = environ.get('SECRET_KEY')
        app.config['SESSION_COOKIE_HTTPONLY'] = environ.get('SESSION_COOKIE_HTTPONLY')
        app.config['SESSION_COOKIE_SECURE'] = environ.get('SESSION_COOKIE_SECURE')
        app.config['SESSION_COOKIE_SAMESITE'] = environ.get('SESSION_COOKIE_SAMESITE')
        app.config['CSRF_COOKIE_NAME'] = environ.get('CSRF_COOKIE_NAME')
        app.config['CSRF_COOKIE_SAMESITE'] = environ.get('CSRF_COOKIE_SAMESITE')
        app.config['CSRF_COOKIE_HTTPONLY'] = environ.get('CSRF_COOKIE_HTTPONLY')
        app.config['CSRF_COOKIE_SECURE'] = environ.get('CSRF_COOKIE_SECURE')
