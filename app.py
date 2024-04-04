from flask import Flask, render_template, request, redirect, session
from flask_sqlalchemy import SQLAlchemy
import bcrypt

app = Flask(__name__)

# Configure MySQL
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+mysqlconnector://root:@localhost/classroomDensityDetectionDB'

# Initialize SQLAlchemy
db = SQLAlchemy(app)

# Secret key for session management
app.secret_key = 'your_secret_key'

# Define User model
class User(db.Model):
    __tablename__ = 'UserDetails'  # Specify the table name
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password = db.Column(db.String(80), nullable=False)
    userType = db.Column(db.String(10), nullable=False)

# Routes
@app.route('/')
def index():
    if 'username' in session:
        return f'Logged in as {session["username"]}<br><a href="/logout">Log out</a>'
    return 'You are not logged in<br><a href="/login">Log in</a>'

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
                session['username'] = username
                return redirect('/')
        
        return 'Invalid username or password'

    return render_template('login.html')

@app.route('/logout')
def logout():
    session.pop('username', None)
    return redirect('/')

if __name__ == '__main__':
    app.run(debug=True)
