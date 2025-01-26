from flask import Flask, render_template, redirect, request, url_for, session, make_response
from flask_sqlalchemy import SQLAlchemy


app = Flask(__name__)
app.config.from_envvar('FLASK_CONFIG')
db = SQLAlchemy(app)

car1 = ["Toyota", "Corolla",15000.0, "Reliable family car."]
car2 = ["BMW", "X5",50000.0, "Luxury SUV with great performance."]
car3 = ["Toyota", "Corolla",15000.0, "Reliable family car."]
car4 = ["BMW", "X5",50000.0, "Luxury SUV with great performance."]
car5 = ["Toyota", "Corolla",15000.0, "Reliable family car."]
car6 = ["BMW", "X5",50000.0, "Luxury SUV with great performance."]
cars=[car1,car2,car3,car4,car5,car6]

@app.errorhandler(404)
def page_not_found(e):
    return make_response(render_template('custom_404.html'), 404)

@app.route("/")
def home():
    username = session.get('username')  # Проверка за наличен потребител
    if username:
        return render_template('home.html', title='Home', my_username=username)
    else:
        return render_template('home.html', title='Home', my_username=None)


@app.route('/catalog')
def catalog():
    return render_template('catalog.html', cars=cars)

@app.route("/login")
def login(message=None):
    if 'message' in request.args:
        message = request.args['message']
    print(message)
    return render_template('login_form.html', title='Login', message=message)

@app.route("/login_action", methods=['POST'])
def login_action():
    if request.method != 'POST':
        return redirect(url_for('/login', message='Invalid method'))

    if request.form['username'] == 'admin' and request.form['password'] == 'admin':
        username = request.form['username']
        session['username'] = username
        return redirect(url_for('home', name=username))
    else:
        return redirect(url_for('login', message='Invalid username or password'))

@app.route('/logout')
def logout():
    session.clear()  
    return redirect(url_for('home')) 

@app.route("/profile/<username>")
def user_page(username):
    username = session.get('username')
    if username:
        return render_template('user.html', title='User', user=username)
    else:
        return redirect(url_for('login', message='Log in your profile!'))

@app.route("/register")
def register(message=None):
    if 'message' in request.args:
        message = request.args['message']
    print(message)
    return render_template('register.html', title='Registration Form', message=message)

@app.route("/register_action", methods=['POST'])
def register_action():
    if request.method != 'POST':
        return redirect(url_for('/register', message='Invalid method'))
    
    username = request.form['username']
    session['username'] = username
    return redirect(url_for('home', name=username))
##################################################################################################
    # if request.form['username'] == 'admin' and request.form['password'] == 'admin':
    #     username = request.form['username']
    #     session['username'] = username
    #     return redirect(url_for('home', name=username))
    # else:
    #     return redirect(url_for('login', message='Invalid username or password'))
##################################################################################################
app.run()