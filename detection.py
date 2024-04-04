import cv2
import os
import numpy as np

# Load YOLO
net = cv2.dnn.readNet("./yoloFiles/yolov3.weights", "./yoloFiles/yolov3.cfg")
classes = []
with open("./yoloFiles/coco.names", "r") as f:
    classes = [line.strip() for line in f.readlines()]
layer_names = net.getLayerNames()
output_layers = [layer_names[i - 1] for i in net.getUnconnectedOutLayers()]

# # Function to detect humans
# def detect_humans(image):
#     height, width, channels = image.shape

#     # Detecting objects
#     blob = cv2.dnn.blobFromImage(image, 0.00392, (416, 416), (0, 0, 0), True, crop=False)
#     net.setInput(blob)
#     outs = net.forward(output_layers)

#     # Counting humans and drawing bounding boxes
#     human_count = 0
#     for out in outs:
#         for detection in out:
#             scores = detection[5:]
#             class_id = np.argmax(scores)
#             confidence = scores[class_id]
#             if confidence > 0.7 and class_id == 0:  # Class ID for person/human is 0
#                 human_count += 1
#                 # Get coordinates for drawing bounding box
#                 center_x = int(detection[0] * width)
#                 center_y = int(detection[1] * height)
#                 w = int(detection[2] * width)
#                 h = int(detection[3] * height)
#                 # Drawing bounding box
#                 x = int(center_x - w / 2)
#                 y = int(center_y - h / 2)
#                 cv2.rectangle(image, (x, y), (x + w, y + h), (0, 255, 0), 2)
#     return human_count


def apply_nms(boxes, scores, threshold=0.5):
    # Convert the boxes list to a NumPy array
    boxes = np.array(boxes)

    # Get indices of sorted scores in descending order
    indices = np.argsort(scores)[::-1]
    keep = []

    while len(indices) > 0:
        i = indices[0]
        keep.append(i)
        xx1 = np.maximum(boxes[i][0], boxes[indices[1:], 0])
        yy1 = np.maximum(boxes[i][1], boxes[indices[1:], 1])
        xx2 = np.minimum(boxes[i][2], boxes[indices[1:], 2])
        yy2 = np.minimum(boxes[i][3], boxes[indices[1:], 3])

        w = np.maximum(0.0, xx2 - xx1 + 1)
        h = np.maximum(0.0, yy2 - yy1 + 1)
        intersection = w * h

        # Calculate IoU (Intersection over Union)
        iou = intersection / (w * h + (boxes[i][2] - boxes[i][0] + 1) * (boxes[i][3] - boxes[i][1] + 1) - intersection)

        # Filter out boxes with IoU greater than the threshold
        indices = indices[1:][iou <= threshold]

    return keep
    
def detect_humans_unique(image,confidenceThreshold):
    height, width, channels = image.shape
    # Detecting objects
    blob = cv2.dnn.blobFromImage(image, 0.00392, (416, 416), (0, 0, 0), True, crop=False)
    net.setInput(blob)
    outs = net.forward(output_layers)

    # Store bounding boxes and scores
    boxes = []
    confidences = []

    for out in outs:
        for detection in out:
            scores = detection[5:]
            class_id = np.argmax(scores)
            confidence = scores[class_id]
            if confidence > confidenceThreshold and class_id == 0:  # Class ID for person/human is 0
                # Get coordinates for drawing bounding box
                center_x = int(detection[0] * width)
                center_y = int(detection[1] * height)
                w = int(detection[2] * width)
                h = int(detection[3] * height)
                # Drawing bounding box
                x = int(center_x - w / 2)
                y = int(center_y - h / 2)
                boxes.append([x, y, x + w, y + h])
                confidences.append(float(confidence))

    # Apply Non-Maximum Suppression
    indices = apply_nms(boxes, confidences)

    # Counting humans and drawing bounding boxes
    human_count = len(indices)
    for i in indices:
        (x, y, x2, y2) = boxes[i]
        cv2.rectangle(image, (x, y), (x2, y2), (0, 255, 0), 2)

    return human_count


## Functionality no. 3.1.1 from SRS - Accessing and Processing Images from CCTV cameras
    # Load image
def getHumanCount(path):
    ## check if path contains the file extension jpeg, jpg or png

    filename, file_extension = os.path.splitext(path)
    if file_extension.lower() not in ('.jpeg', '.jpg', '.png'):        
        print("Incorrect path")
        return None

    image = cv2.imread(path)
    # print(image)
    # image = cv2.imread("./assets/input1.jpg")

    # Detect humans
    human_count = detect_humans_unique(image,0.0)
    print("Number of humans detected:", human_count)

    # Display the image with bounding boxes
    
    # cv2.imshow("Image", image)
    cv2.imwrite("./assets/output.jpg",image)
    # key = -1
    # key = cv2.waitKey(0)

    # if key == 32: 
    #     cv2.destroyAllWindows()  # Close all OpenCV windows
    return human_count

def getCctvImage(className):
    return  f"./assets/cctv/{className}.jpg"

# Test code
# getHumanCount("./assets/cctv.png")
# getHumanCount("./assets/input1.jpg")
# getHumanCount("./assets/input2.jpg")
# getHumanCount("./assets/cctv2.jpg")
# getHumanCount("./assets/cctv3.jpg")
# getHumanCount("./assets/cctv0.jpg")
# getHumanCount("./assets/cctv4.jpg")
# getHumanCount("./assets/metadata1.jpg")
# getHumanCount(".  /assets/metadata2.jpg")
