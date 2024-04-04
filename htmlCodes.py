from flask import url_for

def loginLink():
    return '''
        <style>
            .login-container {
                text-align: center;
            }
            .login-container a {
                display: inline-block; /* Display links side by side */
                margin-right: 10px; /* Add margin between links */
                text-decoration: none; /* Remove default underline */
                color: #007bff; /* Set link color */
            }
            .login-container a:hover {
                text-decoration: underline; /* Underline on hover */
            }
        </style>
        <div class="login-container">
            <p>You are not logged in</p>
            <a href="/login">Log in</a>
            <a href="/signup">Sign Up</a>
        </div>
    '''


def userNotLoggedIn():
    return '''
            <style>
                body {
                    display: flex;
                    justify-content: center;
                    align-items: center;
                    height: 100vh;
                    margin: 0;
                    background-color: #f2f2f2; /* Set background color for the entire page */
                }
                .login-container {
                    text-align: center;
                    border: 2px solid #ccc;
                    padding: 20px;
                    border-radius: 10px;
                    background-color: white; /* Set background color for the centered box */
                }
                .login-container a {
                    display: block;
                    margin-top: 10px;
                }
            </style>
        ''' + loginLink()

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
                padding-top: 20px; /* Add padding to the top */
            }
            #searchBar {
                width: 70%;
                height: 30px; /* Adjust height */
                padding: 5px; /* Add padding */
                border: 2px solid #ccc; /* Add border */
                border-radius: 5px; /* Add border radius */
                margin-bottom: 10px; /* Add margin to the bottom */
            }
            #searchBar:focus {
                outline: none; /* Remove outline on focus */
            }
            #submitBtn {
                padding: 10px 20px; /* Adjust padding */
                border: 2px solid #ccc; /* Add border */
                border-radius: 5px; /* Add border radius */
                cursor: pointer; /* Change cursor on hover */
            }
            #submitBtn:hover {
                background-color: #f0f0f0; /* Light gray background on hover */
            }
        </style>
        <form method="post" class="search-container">
            <input type="text" id="searchBar" name="searchBar" placeholder="Enter Classroom name...">
            <input type="submit" id="submitBtn" value="Submit">
        </form>
    '''
    return logoutButton() + form

def renderErrorMessage(searchValue, classrooms):
    form = renderForm();
    return f'''
        <h3>Incorrect classroom name entered: {searchValue}</h3>
        {form}
        <p>Available classrooms:</p>
        <ul>
            {''.join(f"<li>{classroom}</li>" for classroom in classrooms)}
        </ul>
    '''

def renderResult(searchValue, humanCount, session):
    print(session)
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
            <h1>Recent Search Value: {searchValue}</h1>
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
