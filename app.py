from flask import Flask
from flask_cors import CORS

app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": "*", "methods": ["GET", "POST", "PUT", "DELETE", "OPTIONS"], "allow_headers": ["Content-Type", "Authorization"]}})

from routes import bussinessloan, emailclassify, presonalloan, langchain, company_check,ads

app.register_blueprint(bussinessloan.bl)
app.register_blueprint(emailclassify.email)
app.register_blueprint(presonalloan.ploan)
app.register_blueprint(langchain.ln)
app.register_blueprint(company_check.cp)
app.register_blueprint(ads.ads)
@app.route('/', methods=['GET'])
def hello_world():
    return 'Azure Server is running!'


if __name__ == '__main__':
    app.run(debug=True)
