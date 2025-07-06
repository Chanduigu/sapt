from flask import Flask
from routes.auth import auth_bp
from routes.admin import admin_bp
from routes.billing import billing_bp

import os

app = Flask(__name__)
app.secret_key = 'sapthagiri-foods'  

app.register_blueprint(auth_bp)
app.register_blueprint(admin_bp)
app.register_blueprint(billing_bp)

if __name__ == '__main__':
    app.run(debug=True)
