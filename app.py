from flask import Flask, render_template, redirect, url_for, request,session
from detection import getHumanCount, getCctvImage
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
from flask_sqlalchemy import SQLAlchemy
import bcrypt
from htmlCodes import userNotLoggedIn,renderErrorMessage,renderForm,renderResult, loginLink

app = Flask(__name__, template_folder='./templates', static_folder='./assets/')
app.config['SECRET_KEY'] = 'doyougetdejavu?'

# Configure MySQL
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+mysqlconnector://root:@localhost/classroomDensityDetectionDB'

# Initialize SQLAlchemy
db = SQLAlchemy(app)

# Secret key for session management
app.secret_key = 'justHowFastTheNightChanges!'

classrooms = [
                'AC101', 'AC102', 'AC103', 'AC104',
                'AC201', 'AC202', 'AC203', 'AC204',
             ]

# Define User model
class User(db.Model):
    __tablename__ = 'UserDetails'  # Specify the table name
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password = db.Column(db.String(80), nullable=False)
    userType = db.Column(db.String(10), nullable=False)


@app.route('/', methods=['GET', 'POST'])
def search():
    if 'user' not in session:
        return userNotLoggedIn()

    path = ""
    humanCount = 0
    htmlString = renderForm() 
    
    if request.method == 'POST':
        searchValue = request.form['searchBar']
        print("Search value:", searchValue)
        if(searchValue not in classrooms):
            htmlString = renderErrorMessage(searchValue,classrooms)
        else:
            path=f"./assets/cctv/{searchValue}.jpg"
            humanCount = getHumanCount(path)
            htmlString = renderResult(searchValue,humanCount, session)
    
    return htmlString

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        userType = request.form['userType']

        # Check if username already exists
        user = User.query.filter_by(username=username).first()

        if user:
            return 'Username already exists'

        # Hash the password
        hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())

        new_user = User(username=username, password=hashed_password, userType=userType)
        db.session.add(new_user)
        db.session.commit()

        session['username'] = username
        session['userType'] = userType
        return redirect('/')
    return render_template('signup.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        # Retrieve the user from the database
        user = User.query.filter_by(username=username).first()

        if user:
            # Check if the provided password matches the hashed password
            if bcrypt.checkpw(password.encode('utf-8'), user.password.encode('utf-8')):
                # Successfully logged in, you can access the entire user tuple here
                session['user'] = {
                    'id': user.id,
                    'username': user.username,
                    'userType': user.userType
                }
                return redirect('/')
        
        return 'Invalid username or password' + loginLink()

    return render_template('login.html')

@app.route('/logout', methods=['GET', 'POST'])
def logout():
    if request.method == 'POST':
        session.pop('user', None)
    return redirect('/')

if __name__ == '__main__':
    app.run(debug=True)