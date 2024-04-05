from flask import Flask, render_template, redirect, url_for, request,session
from detection import getHumanCount, getCctvImage
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
from flask_sqlalchemy import SQLAlchemy
import bcrypt
from htmlCodes import userNotLoggedIn,renderErrorMessage,renderForm,renderResult, invalidCredentialsMessage, loginLink, unauthorized_access_message
from sqlalchemy import inspect
from datetime import datetime
import pytz

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

class UserSearchHistory(db.Model):
    __tablename__ = 'UserSearchHistory'

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(255), nullable=False)
    classname = db.Column(db.String(255), nullable=False)
    density = db.Column(db.Integer, nullable=False)
    timestamp = db.Column(db.TIMESTAMP, nullable=False, default=db.func.current_timestamp())

    def __repr__(self):
        return f"<UserSearchHistory id={self.id}, username={self.username}, classname={self.classname}, density={self.density}, timestamp={self.timestamp}>"

def create_tables_if_not_exists():
    # List of all defined models
    models = [User, AssignedClassroom, UserSearchHistory]
    
    # Get table names from the defined models
    table_names = [model.__tablename__ for model in models]
    
    # Get existing table names from the database
    inspector = inspect(db.engine)
    existing_table_names = inspector.get_table_names()
    
    # Check if each table exists, and create it if it does not
    for model in models:
        table_name = model.__tablename__
        if table_name not in existing_table_names:
            print(f"Creating table '{table_name}'")
            model.__table__.create(bind=db.engine)

@app.route('/', methods=['GET', 'POST'])
def search():
    create_tables_if_not_exists()
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

    if request.method == 'POST':
        searchValue = request.form['searchBar']
        print("Search value:", searchValue)
        if searchValue not in classrooms:
            htmlString = renderErrorMessage(searchValue, classrooms, facultyClassrooms)
        else:
            path = f"./assets/cctv/{searchValue}.jpg"
            humanCount = getHumanCount(path)
            
            # Update search history in session
            for entry in session['searchHistory']:
                if entry[0] == searchValue:
                    entry[1] = humanCount
                    break
            else:
                session['searchHistory'] += [[searchValue, humanCount]]
                
            # Create and add entry to UserSearchHistory table
            if 'user' in session:
                username = session['user']['username']
                search_history_entry = UserSearchHistory(username=username, classname=searchValue, density=humanCount)
                db.session.add(search_history_entry)
                db.session.commit()
            
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

        if username == '' or password == ''  or firstName == '' or lastName == '':
            return 'Please fill out all fields.' + loginLink()
        # Check if username already exists
        user = User.query.filter_by(username=username).first()

        if user:
            return 'Username already exists' + loginLink()

        # Hash the password
        hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())

        new_user = User(username=username, password=hashed_password, firstName=firstName, lastName=lastName, userType=userType)
        db.session.add(new_user)
        db.session.commit()
        print()
        session['user'] = {
            'id': new_user.id,
            'username': new_user.username,
            'userType': new_user.userType,
            'firstName': new_user.firstName,
            'lastName': new_user.lastName
        }
        session['searchHistory'] = []
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
        
        return invalidCredentialsMessage

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


def deleteRecords_in_range(classroom, start_datetime, end_datetime):
    try:
        start_datetime_utc = pytz.utc.localize(start_datetime)
        if end_datetime == None:
            db.session.query(UserSearchHistory).filter(
                UserSearchHistory.classname == classroom,
                UserSearchHistory.timestamp >= start_datetime_utc,
            ).delete()
        else:
            end_datetime_utc = pytz.utc.localize(end_datetime)
            # Perform deletion operation
            db.session.query(UserSearchHistory).filter(
                UserSearchHistory.classname == classroom,
                UserSearchHistory.timestamp >= start_datetime_utc,
                UserSearchHistory.timestamp <= end_datetime_utc
            ).delete()
        # Commit the transaction
        db.session.commit()
        
        return True  # Deletion successful
    except Exception as e:
        # Rollback the transaction in case of an error
        db.session.rollback()
        print(f"Error occurred while deleting records: {e}")
        return False  # Deletion failed


@app.route('/deleteRecords', methods=['POST'])
def deleteRecords():
    if 'user' not in session or session['user']['userType'] != 'admin':
        return unauthorized_access_message()  

    classroom = request.form.get('classroom')
    start_date = request.form.get('start_date')
    end_date = request.form.get('end_date')

    if start_date == '':
        message = 'Deleting Failed'
        error = 'Date Range cannot be empty'
    elif end_date == '':    # start date is not so delete all
        start_datetime = datetime.strptime(start_date, "%Y-%m-%dT%H:%M")
        date_string = '1970-01-01 23:59:59'
        date_object = datetime.strptime(date_string, '%Y-%m-%d %H:%M:%S')

        print('\n\n\n\n\n')
        print(start_datetime)
        print(date_object)
        print(start_datetime < date_object)
        print('\n\n\n\n\n')
        if start_datetime < date_object:
            print('Inside 1970s function')
            result = deleteRecords_in_range(classroom, start_datetime, None)
            message = 'All Records Deleted successfully'
            error = ''
        else:
            message = 'Records Deleting Failed'
            error = 'to delete all records set startDate to 01/01/1970'
    else:
        # Parse start_date and end_date strings into datetime objects
        start_datetime = datetime.strptime(start_date, "%Y-%m-%dT%H:%M")
        end_datetime = datetime.strptime(end_date, "%Y-%m-%dT%H:%M")

        # Perform deletion operation in the database
        result = deleteRecords_in_range(classroom, start_datetime, end_datetime)
        print(result)
        # Redirect to a success page or perform any other necessary action
        message = "Records deleted successfully" 
    return render_template('assignmentResult.html', message=message, error=error)

if __name__ == '__main__':
    app.run(debug=True)