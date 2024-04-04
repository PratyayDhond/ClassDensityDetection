from flask import Flask, render_template, redirect, url_for, request
from detection import getHumanCount, getCctvImage
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField

app = Flask(__name__, template_folder='./templates')
app.config['SECRET_KEY'] = 'doyougetdejavu?'

classrooms = [
                'AC101', 'AC102', 'AC103', 'AC104',
                'AC201', 'AC202', 'AC203', 'AC204'             
             ]

@app.route('/', methods=['GET', 'POST'])
def hello_world():

    path = "./assets/cctv/"
    human_count = getHumanCount(path)
    print(human_count)
    htmlString = f'''
            <form method="post">
                <input type="text" id="searchBar" name="searchBar" placeholder="Enter Classroom name...">
                <input type="submit" value="Submit">
            </form>
           '''    
    
    if request.method == 'POST':
        searchValue = request.form['searchBar']
        print("Search value:", searchValue)
        if(searchValue not in classrooms):
            htmlString += f'<h3> Incorrect classroom name entered. </h3>'
            htmlString += f'<ul>'
            for i in range(0,len(classrooms)):
                htmlString += f'<li>{classrooms[i]}</li> </br>'
            htmlString += f'</ul>'
        else:
            path=f"./assets/cctv/{searchValue}.jpg"
            human_count = getHumanCount(path)
            htmlString = f'''
                <h1>Hello, World! This world has {str(human_count)} humans!</h1>
                <form method="post">
                    <input type="text" id="searchBar" name="searchBar" placeholder="Enter Classroom name...">
                    <input type="submit" value="Submit">
                </form>
            '''
            htmlString += f"<h1>Search Value : {searchValue}</h1>"
    
    return htmlString

if __name__ == '__main__':
    app.run(debug=True)