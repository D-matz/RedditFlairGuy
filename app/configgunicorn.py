#gunicorn config
wsgi_app = "RSOEndpoint:app"
workers = 2
bind = "0.0.0.0:443"

certfile = 'fullchain.pem'
keyfile = 'privkey.pem'
