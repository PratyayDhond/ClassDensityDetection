from flask import Flask
from detection import getHumanCount

app = Flask(__name__)

@app.route('/')
def hello_world():
    path= "./assets/cctv0.jpg"
    human_count = getHumanCount(path)
                # <img src=static/cctv0.jpg" alt="cctv image">        
    return  f'''
                <h1>Hello, World! This world has {str(human_count)} humans!</h1>
            '''


if __name__ == '__main__':
    app.run(debug=True)




# import base64
# import io

# from detection import detect_humans

# def hello_world():
#     image_path = "./assets/cctv0.jpg"
#     image = cv2.imread(image_path)
#     human_count = detect_humans(image)

#     # Convert the image to a base64-encoded string
#     image_bytes = cv2.imencode('.png', image)[1]
#     base64_image = base64.b64encode(image_bytes).decode()

#     return f'''
# <html>
#   <head>
#     <title>Hello, World!</title>
#   </head>
#   <body>
#     <h1>Hello, World! This world has {human_count[0]} humans!</h1>
#     <img src="data:image/png;base64,{base64_image}" alt="Image of the scene">
#   </body>
# </html>
# '''

# if __name__ == '__main__':
#     app.run(debug=True)