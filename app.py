from flask import Flask, render_template, redirect, url_for, request,session
from detection import getHumanCount, getCctvImage
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
from flask_sqlalchemy import SQLAlchemy
import bcrypt

app = Flask(__name__, template_folder='./templates', static_folder='./assets/')
app.config['SECRET_KEY'] = 'doyougetdejavu?'

# Configure MySQL
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+mysqlconnector://root:@localhost/classroomDensityDetectionDB'

# Initialize SQLAlchemy
db = SQLAlchemy(app)

# Secret key for session management
app.secret_key = 'your_secret_key'

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


def logoutButton():
    return '''
        <div style="height:20px">
        <form action="/logout" method="post" style="position: fixed; top: 10px; right: 10px;">
            <input type="submit" value="Logout">
        </form>
        </div>
    '''

def renderForm():
    form = '''
        <style>
            .search-container {
                width: 50%;
                margin: 0 auto;
                text-align: center;
            }
            #searchBar {
                width: 70%;
                height: 3%;
            }
        </style>
        <form method="post" class="search-container">
            <input type="text" id="searchBar" name="searchBar" placeholder="Enter Classroom name...">
            <input type="submit" value="Submit">
        </form>
    '''
    return logoutButton() + form




def renderErrorMessage(searchValue):
    form = renderForm();
    return f'''
        <h3>Incorrect classroom name entered: {searchValue}</h3>
        {form}
        <p>Available classrooms:</p>
        <ul>
            {''.join(f"<li>{classroom}</li>" for classroom in classrooms)}
        </ul>
    '''

def renderResult(searchValue, humanCount):
    htmlString = '''
        <style>
            .search-container {
                width: 50%;
                margin: 0 auto;
                text-align: center;
            }
            #searchBar {
                width: 70%;
                height: 3%;
            }
            .classroom-list {
                list-style: none;
                padding: 0;
                display: flex;
                flex-wrap: wrap;
                justify-content: space-between;
            }
            .classroom-list li {
                width: 22%;
                margin-bottom: 10px;
                padding: 5px;
                box-sizing: border-box;
                text-align: center;
            }
            .classroom-container {
                max-width: 160px;
                margin: 0 auto;
            }
            .classroom-image-div {
                width:100vw;
                display: block;
            }
            .classroom-image {
                width: 70vw;
                padding-left: 15vw;
            }
        </style> '''
    htmlString += f'''
        <h1>This classroom has at least {humanCount} students!</h1>
        <div class="search-container">
            <form method="post">
                <input type="text" id="searchBar" name="searchBar" placeholder="Enter Classroom name...">
                <input type="submit" value="Submit">
            </form>
            <h1>Search Value: {searchValue}</h1>
        </div>
        '''
    
    if session['user']['userType'] != 'student': # if the user is not student allow the visibility of the labelled cctv image as well
        image_url = url_for('static', filename="output.jpg")
        htmlString +=   f'''
                            <div class="classroom-image-div">
                                <img src="{image_url}"  class="classroom-image" alt="Classroom Image">
                            </div>
                        '''
    return logoutButton() + htmlString

@app.route('/', methods=['GET', 'POST'])
def search():
    if 'user' not in session:
        return 'You are not logged in<br><a href="/login">Log in</a>'
    # print("\n\n\\n\n\n\n\n\n\\n\n\n")
    # print(session['user']['userType'])
    # print("\n\n\\n\n\n\n\n\n\\n\n\n")
    path = ""
    humanCount = 0
    htmlString = renderForm() 
    
    if request.method == 'POST':
        searchValue = request.form['searchBar']
        print("Search value:", searchValue)
        if(searchValue not in classrooms):
            htmlString = renderErrorMessage(searchValue)
        else:
            path=f"./assets/cctv/{searchValue}.jpg"
            humanCount = getHumanCount(path)
            htmlString = renderResult(searchValue,humanCount)
    
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
        
        return 'Invalid username or password'

    return render_template('login.html')

@app.route('/logout', methods=['GET', 'POST'])
def logout():
    if request.method == 'POST':
        session.pop('user', None)
        return redirect('/')
    else:
        # Handle GET request (if needed)
        return 'Logout page'

if __name__ == '__main__':
    app.run(debug=True)