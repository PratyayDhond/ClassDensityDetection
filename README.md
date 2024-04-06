
Download the YOLO files

YOLO TINY recommended for human detection 
https://github.com/pjreddie/darknet/blob/master/cfg/yolov3-tiny.cfg
https://github.com/smarthomefans/darknet-test/blob/master/yolov3-tiny.weights
https://github.com/smarthomefans/darknet-test/blob/master/coco.names

The assets are being uploaded to the github repo temporarily for testing purposes

You will need to create a virtual environment in the repo itself using the following commands

```python -m venv venv```

to execute and move into the virtual env

```source venv/bin/activate```


### To install the dependencies
```pip install -r requirements.txt```

### DB Setup
 To Setup the database in mysql, import or execute the 'dbschema.sql' file located in the root directory
ALTER USER 'root'@'localhost' IDENTIFIED WITH mysql_native_password BY 'Current-Root-Password';
