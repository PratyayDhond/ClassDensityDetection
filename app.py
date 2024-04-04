from flask import Flask, render_template, redirect, url_for, request, send_from_directory
from detection import getHumanCount, getCctvImage
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField

app = Flask(__name__, template_folder='./templates', static_folder='./assets/')
app.config['SECRET_KEY'] = 'doyougetdejavu?'

classrooms = [
                'AC101', 'AC102', 'AC103', 'AC104',
                'AC201', 'AC202', 'AC203', 'AC204',             
             ]

def renderForm():
    return '''
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
    image_url = url_for('static', filename="output.jpg")
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
        <div class="classroom-image-div">
            <img src="{image_url}"  class="classroom-image" alt="Classroom Image">
        </div>
    '''
    return htmlString

@app.route('/', methods=['GET', 'POST'])
def search():

    path = "./static/cctv0.jpg"
    humanCount = getHumanCount(path)
    print(humanCount)
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

if __name__ == '__main__':
    app.run(debug=True)