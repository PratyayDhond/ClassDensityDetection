from flask import url_for,session

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

def backgroundImage():
    return '''
                <style>
                    .background-image-coep {
                        position: absolute;
                        top: 0;
                        left: 0;
                        width: 100%;
                        height: 100%;
                        object-fit: cover; /* Stretch to fit */
                        z-index: -2; /* Send to the back */
                    }
                    .overlay {
                        position: absolute;
                        top: 0;
                        left: 0;
                        width: 100%;
                        height: 100%;
                        background-color: rgba(255, 255, 255, 0.35); /* Adjust opacity here */
                        z-index:-1
                    }
                </style>
                <img src="/assets/coep.jpg" alt="Background Image" class="background-image-coep">
                <div class="overlay"></div>
            '''

def userNotLoggedIn():
    return backgroundImage() + '''
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
                    background-color: rgba(255, 255, 255, 0.7); /* Set background color for the centered box */
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

def adminRedirectButton():
    if 'user' in session and session['user']['userType'] == 'admin':
        return '''
            <div style="height:20px">
            <form action="/admin" method="get" style="position: fixed; top: 10px; right: 80px;">
                <input type="submit" value="Admin Page">
            </form>
            </div>
        '''
    else:
        return ''

def getUserName():
    if 'user' in session:
        # print(session)
        firstName = session['user']['firstName']
        lastName = session['user']['lastName']
        return [firstName, lastName]
    return []

def WelcomeMessage():
    htmlString = ""
    userName = getUserName()
    htmlString += '<p style="text-align: center;"><span style="padding:4px; font-weight: bold; display: inline-block;"> Welcome '
    if userName[0] == '' and userName[1] == '':
        htmlString += 'Admin'
    else:
        htmlString += userName[0] + ' ' + userName[1]
    htmlString += '! </span></p>'
    return htmlString


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
    htmlString =  WelcomeMessage()
    htmlString += adminRedirectButton() + logoutButton() + form
    return htmlString # + backgroundImage() 

def renderErrorMessage(searchValue, classrooms, facultyClassrooms):
    form = renderForm();
    htmlString = f'''
        <body style="background-color: #f2f2f2;">
            <div style="width: 50%; margin: 0 auto; border: 2px solid #ccc; background-color: #f2f2f2; padding: 20px; text-align: center;">
                {form}
                <p style="font-weight: bold; color: red;">Incorrect classroom name entered {searchValue}</p>
        '''
    if len(facultyClassrooms) > 0:  
        facultyClassrooms.sort
        htmlString +=   f'''
                <p>Classrooms allotted to you:</p>
                <ul style="list-style: none; padding: 0;"> <!-- Remove default list bullets and padding -->
                    {''.join(f"<li>{classroom}</li>" for classroom in facultyClassrooms)}
                </ul>
            '''
        
    htmlString += f'''
                <p>All Available classrooms:</p>
                <ul style="list-style: none; padding: 0;"> <!-- Remove default list bullets and padding -->
                    {''.join(f"<li>{classroom}</li>" for classroom in classrooms)}
                </ul>
            </div>
        '''

    htmlString += previousSearches(searchValue)
    htmlString += '</body>'
    return htmlString


def previousSearches(searchValue):
    htmlString = ""
    if 'searchHistory' in session:
        htmlString += '<div style="background-color: #f2f2f2;width: 50%; margin: 0 auto; border: 2px solid #ccc; padding: 20px; text-align: center;">'
        htmlString += '<p style="font-weight: bold;">Previous Search Values:</p>'
        # Iterate over each search entry in the search history
        for search_entry in session['searchHistory']:
            value, density = search_entry
            # Construct HTML elements for each search entry and append to the HTML string
            if value != searchValue:
                htmlString += f"<p>Search Value: {value}, Density: {density}</p>"
        htmlString += '</div>'
    else:
        # If search history doesn't exist, display a message
        htmlString += "<p>No search history available.</p>"
    return htmlString


def renderResult(searchValue, humanCount, facultyClassrooms):
    # print(session)
    htmlString = WelcomeMessage()
    htmlString += '''
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
                            width: 100%;
                            text-align: center;
                        }
                        .classroom-image {
                            max-width: 100%;
                        }
                        .result-container {
                        width: 50%;
                        margin: 0 auto;
                        text-align: center;
                        border: 2px solid #ccc;
                        padding: 20px;
                    }
                </style> '''
    htmlString += f'''
        <div class="result-container" style="background-color: #f2f2f2;">
            <h1>This classroom has at least {humanCount} students!</h1>
            <div class="search-container">
                <form method="post">
                    <input type="text" id="searchBar" name="searchBar" placeholder="Enter Classroom name...">
                    <input type="submit" value="Submit">
                </form>
                <h1>Recent Search Value: {searchValue}</h1>
            </div>
    '''
    # if session['user']['userType'] == 'admin' : # if the user is not student allow the visibility of the labelled cctv image as well
    # if the user is admin they should be by default allowed to view all the details and images
    # if the user is not admin then
    #       if the user is student then the facultyClassrooms array would be empty
    #       if the user is faculty then the facultyClassrooms array would only have the classrooms assigned to the faculty
    if session['user']['userType'] == 'admin' or searchValue in facultyClassrooms:  
        image_url = url_for('static', filename="output.jpg")
        htmlString +=   f'''
            <div class="classroom-image-div">
                <img src="{image_url}" class="classroom-image" alt="Classroom Image">
            </div>
        '''


    # Appending the results of previous searches here
    htmlString += previousSearches(searchValue)

    htmlString += '</div>'  # Close the result-container div

    return adminRedirectButton() + logoutButton() + htmlString

def invalidCredentialsMessage():
    html_string = '''
        <div style="width: 50%; margin: 0 auto; border: 2px solid #ccc; padding: 20px; text-align: center; background-color: #f2f2f2;">
            <p style="color: red;">Invalid username or password</p>
            ''' + loginLink() + '''
        </div>
    '''
    return html_string

def unauthorized_access_message():
    return '''
        <!DOCTYPE html>
        <html lang="en">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>Unauthorized Access</title>
            <style>
                body {
                    display: flex;
                    justify-content: center;
                    align-items: center;
                    height: 100vh;
                    margin: 0;
                    background-color: #f2f2f2; /* Set background color for the entire page */
                }
                .message-container {
                    width: 300px; /* Set width of the message container */
                    padding: 20px;
                    border: 2px solid #ccc; /* Add border */
                    border-radius: 10px;
                    background-color: white; /* Set background color for the message container */
                    text-align: center; /* Center align text */
                }
                .login-link {
                    display: block; /* Make login link a block element */
                    margin-top: 10px; /* Add some margin */
                    text-decoration: none; /* Remove underline from link */
                    color: #007bff; /* Set link color */
                }
                .login-link:hover {
                    color: #0056b3; /* Change link color on hover */
                }
            </style>
        </head>
        <body>
            <div class="message-container">
                <p>Unauthorized access detected.</br> Error code: 401</p>
                <a href="/login" class="login-link">Login</a>
            </div>
        </body>
        </html>
    '''
