import cv2
import numpy as np
import json
import easyocr

def blur_except_boxes(image_path, boxes, blur_strength=25):
    image = cv2.imread(image_path)
    mask = np.zeros(image.shape[:2], dtype=np.uint8)

    for box in boxes:
        x, y, w, h = box
        cv2.rectangle(mask, (x, y), (x+w, y+h), 255, -1)
    
    inv_mask = cv2.bitwise_not(mask)

    blurred = cv2.GaussianBlur(image, (99, 99), sigmaX=30, sigmaY=30)

    result = np.where(mask[:,:,None] == 255, image, blurred)
    
    return result

# Function to extract bounding boxes coordinates from JSON data
def extract_boxes(json_data):
    regions = json_data['_via_img_metadata']['sample.jpeg1692900']['regions']
    boxes = []
    for region in regions:
        if region['shape_attributes']['name'] == 'rect':
            x = region['shape_attributes']['x']
            y = region['shape_attributes']['y']
            w = region['shape_attributes']['width']
            h = region['shape_attributes']['height']
            boxes.append((x, y, w, h))
    return boxes

json_file = 'image_heading_annotation.json'  # Replace with your JSON filename
with open(json_file) as f:
    data1 = json.load(f)

json_file = 'image_sub_annotation2.json'  # Replace with your JSON filename
with open(json_file) as f:
    data2 = json.load(f)

heading_boxes = extract_boxes(data1)
subheading_boxes = extract_boxes(data2)

# Blur for headings
result_headings = blur_except_boxes('sample.jpeg', heading_boxes)
cv2.imwrite('blurred_except_headings.jpg', result_headings)

# Blur for subheadings
result_subheadings = blur_except_boxes('sample.jpeg', subheading_boxes)
cv2.imwrite('blurred_except_subheadings.jpg', result_subheadings)

# Create dictionary mapping bounding boxes
box_mapping = dict(zip(heading_boxes, subheading_boxes))

# Use easyocr to extract text from the blurred images
reader = easyocr.Reader(['en'])

def sort_boxes_two_columns(boxes, image_width):
    """Sort boxes in two columns, from top to bottom in each column."""
    mid_x = image_width / 2

    left_column = [box for box in boxes if box[0] < mid_x]
    right_column = [box for box in boxes if box[0] >= mid_x]

    left_column_sorted = sorted(left_column, key=lambda b: b[1])
    right_column_sorted = sorted(right_column, key=lambda b: b[1])
    
    return left_column_sorted + right_column_sorted

def extract_text_from_boxes(image_path, boxes):
    """Extracts text from specific bounding boxes in an image using EasyOCR."""
    image = cv2.imread(image_path)
    reader = easyocr.Reader(['en'])
    extracted_texts = []

    for box in boxes:
        x, y, w, h = box
        cropped_image = image[y:y+h, x:x+w]
        result = reader.readtext(cropped_image)
        text = " ".join([res[1] for res in result])
        extracted_texts.append(text)

    return extracted_texts

def extract_boxes(json_data):
    """Extracts bounding boxes from the given JSON data."""
    regions = json_data['_via_img_metadata']['sample.jpeg1692900']['regions']
    boxes = []
    for region in regions:
        if region['shape_attributes']['name'] == 'rect':
            x = region['shape_attributes']['x']
            y = region['shape_attributes']['y']
            w = region['shape_attributes']['width']
            h = region['shape_attributes']['height']
            boxes.append((x, y, w, h))
    return boxes

# Load the JSON data
with open('image_heading_annotation.json') as f:
    data1 = json.load(f)
with open('image_sub_annotation2.json') as f:
    data2 = json.load(f)

# Get image dimensions (assuming both images have the same dimensions)
image = cv2.imread('blurred_except_headings.jpg')
image_height, image_width = image.shape[:2]

# Extract and sort boxes
heading_boxes = sort_boxes_two_columns(extract_boxes(data1), image_width)
subheading_boxes = sort_boxes_two_columns(extract_boxes(data2), image_width)

# Extract text from the heading and subheading images
heading_texts = extract_text_from_boxes('blurred_except_headings.jpg', heading_boxes)
subheading_texts = extract_text_from_boxes('blurred_except_subheadings.jpg', subheading_boxes)

# Create a dictionary mapping the recognized heading text to subheading text
box_mapping = dict(zip(heading_texts, subheading_texts))

#Coverting to json and printing the output 
json_mapping = json.dumps(box_mapping, indent=2)
print(json_mapping)
