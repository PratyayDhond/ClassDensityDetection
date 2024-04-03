import cv2
import numpy as np

# Load YOLO
net = cv2.dnn.readNet("./yoloFiles/yolov3-tiny.weights", "./yoloFiles/yolov3-tiny.cfg")
classes = []
with open("./yoloFiles/coco.names", "r") as f:
    classes = [line.strip() for line in f.readlines()]
layer_names = net.getLayerNames()
output_layers = [layer_names[i - 1] for i in net.getUnconnectedOutLayers()]

# Function to detect humans
def detect_humans(image):
    height, width, channels = image.shape

    # Detecting objects
    blob = cv2.dnn.blobFromImage(image, 0.00392, (416, 416), (0, 0, 0), True, crop=False)
    net.setInput(blob)
    outs = net.forward(output_layers)

    # Counting humans and drawing bounding boxes
    human_count = 0
    for out in outs:
        for detection in out:
            scores = detection[5:]
            class_id = np.argmax(scores)
            confidence = scores[class_id]
            if confidence > 0.5 and class_id == 0:  # Class ID for person/human is 0
                human_count += 1
                # Get coordinates for drawing bounding box
                center_x = int(detection[0] * width)
                center_y = int(detection[1] * height)
                w = int(detection[2] * width)
                h = int(detection[3] * height)
                # Drawing bounding box
                x = int(center_x - w / 2)
                y = int(center_y - h / 2)
                cv2.rectangle(image, (x, y), (x + w, y + h), (0, 255, 0), 2)
    return human_count

# Load image
image = cv2.imread("./assets/input1.jpg")

# Detect humans
human_count = detect_humans(image)
print("Number of humans detected:", human_count)

# Display the image with bounding boxes
cv2.imshow("Image", image)
cv2.waitKey(0)
cv2.destroyAllWindows()
