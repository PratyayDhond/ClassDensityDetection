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
facultyClassrooms = []

# Define User and Classroom models (assuming you already have these defined)
class User(db.Model):
    __tablename__ = 'UserDetails'  # Specify the table name
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password = db.Column(db.String(80), nullable=False)
    firstName = db.Column(db.String(80), nullable=False)
    lastName = db.Column(db.String(80), nullable=False)
    userType = db.Column(db.String(10), nullable=False)


class AssignedClassroom(db.Model):
    __tablename__ = 'assignedClassroom'  # Specify the table name
    id = db.Column(db.Integer, primary_key=True)
    faculty_id = db.Column(db.Integer, nullable=False)
    classroom = db.Column(db.String(20), nullable=False)

@app.route('/', methods=['GET', 'POST'])
def search():
    if 'user' not in session:
        return userNotLoggedIn()

    path = ""
    humanCount = 0
    htmlString = renderForm()

    # Assuming 'userType' is stored in the session when the user logs in
    user_type = session['user']['userType']
    
    if user_type == 'faculty':
        # Fetch assigned classrooms for faculty
        faculty_id = session['user']['id']
        assigned_classrooms = AssignedClassroom.query.filter_by(faculty_id=faculty_id).all()
        facultyClassrooms = [assignment.classroom for assignment in assigned_classrooms]
    else:
        facultyClassrooms = []

    # Initialize search history in session if not already present

    if request.method == 'POST':
        searchValue = request.form['searchBar']
        print("Search value:", searchValue)
        if searchValue not in classrooms:
            htmlString = renderErrorMessage(searchValue, classrooms, facultyClassrooms)
        else:
            path = f"./assets/cctv/{searchValue}.jpg"
            humanCount = getHumanCount(path)
            
            for entry in session['searchHistory']:
                if entry[0] == searchValue:
                    entry[1] = humanCount
                    break
            else:
                session['searchHistory'] += [[searchValue, humanCount]]
            # print(session['searchHistory']  )
            htmlString = renderResult(searchValue, humanCount, facultyClassrooms)

    return htmlString


@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        firstName = request.form['firstName']
        lastName = request.form['lastName']
        userType = request.form['userType']

        # Check if username already exists
        user = User.query.filter_by(username=username).first()

        if user:
            return 'Username already exists'

        # Hash the password
        hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())

        new_user = User(username=username, password=hashed_password, firstName=firstName, lastName=lastName, userType=userType)
        db.session.add(new_user)
        db.session.commit()

        session['user'] = {
            'id': user.id,
            'username': user.username,
            'userType': user.userType,
            'firstName': user.firstName,
            'lastName': user.lastName
        }
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
                    'userType': user.userType,
                    'firstName': user.firstName,
                    'lastName': user.lastName
                }
                session['searchHistory'] = []
                return redirect('/')
        
        return 'Invalid username or password' + loginLink()

    return render_template('login.html')

@app.route('/logout', methods=['GET', 'POST'])
def logout():
    if request.method == 'POST':
        print(str(session.keys()) + '\n\n\n\n\n\n' + str(session))
        session.pop('user', None)
        session.pop('searchHistory',None)
    return redirect('/')

@app.route('/admin')
def admin():
    # Retrieve faculties and classrooms from the database
    faculties = User.query.filter_by(userType='faculty').all()
    classrooms = ['AC101', 'AC102', 'AC103', 'AC104', 'AC201', 'AC202', 'AC203', 'AC204']  # Retrieve from the database if needed

    return render_template('admin.html', faculties=faculties, classrooms=classrooms)

@app.route('/assign', methods=['POST'])
def assign_classroom():
    faculty_id = request.form['faculty']
    classroom = request.form['classroom']

    # Check if the assignment already exists for the faculty_id and classroom
    existing_assignment = AssignedClassroom.query.filter_by(faculty_id=faculty_id, classroom=classroom).first()
    if existing_assignment:
        message = 'Classroom is already assigned'
    else:
        # Save the assignment to the database
        assignment = AssignedClassroom(faculty_id=faculty_id, classroom=classroom)
        db.session.add(assignment)
        db.session.commit()
        message = 'Classroom assigned successfully'

    return render_template('assignmentResult.html', message=message)



if __name__ == '__main__':
    app.run(debug=True)