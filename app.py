from flask import Flask, request, jsonify, make_response, render_template, session
import jwt
from datetime import datetime, timedelta
from functools import wraps

app = Flask(__name__)
app.config['SECRET_KEY'] = '7cadb2fc63e04aed89280bf7b6f5c05c'

def token_required(func):
    @wraps(func)
    def decorated(*args, **kwargs):
        token = request.args.get('token')
        if not token:
            return jsonify({'Alert': 'Token is missing!'})
        try:
            payload = jwt.decode(token, app.config['SECRET_KEY'])
        except jwt.ExpiredSignatureError:
            return jsonify({'Alert': 'Token has expired'})
        except jwt.InvalidTokenError:
            return jsonify({'Alert': 'Invalid Token'})
        return func(*args, **kwargs)
    return decorated

@app.route('/')
def home():
    if not session.get('logged_in'):
        return render_template('login.html')
    else:
        return 'Already logged in'

@app.route('/public')
def public():
    return 'For Public'

@app.route('/auth')
@token_required
def auth():
    return 'JWT is verified. Welcome to dashboard'

@app.route('/login', methods=['POST'])
def login():
    if request.form['username'] == 'admin' and request.form['password'] == '123456':
        session['logged_in'] = True
        token = jwt.encode({
            'user': request.form['username'],
            'exp': datetime.utcnow() + timedelta(seconds=120)
        }, app.config['SECRET_KEY'])
        return jsonify({'token': token})
    else:
        return make_response('Unable to verify', 403, {'WWW-Authenticate': 'Basic realm="Authentication failed"'})

if __name__ == '__main__':
    app.run(debug=True)
