import os
import cv2
import time
from ultralytics import YOLO
import numpy as np

# Load YOLO model
model = YOLO("125ImageSetYolov8X.pt")
model_name = "125ImageSetYolov8X"  # Name of your model

# Setup directories
input_folder = "inputFolder"
analysed_dir = os.path.join(os.getcwd(), 'analysed')
os.makedirs(analysed_dir, exist_ok=True)  # This will create the directory if it does not exist
cropped_dir = os.path.join(analysed_dir, 'cropped')
os.makedirs(cropped_dir, exist_ok=True)  # This will create the directory for cropped images

confidence_threshold = 0.50  # Confidence threshold
processed_files = set()  # Track processed files to avoid re-processing

def process_image(filename):
    image_path = os.path.join(input_folder, filename)
    results = model(image_path)
    img = cv2.imread(image_path)
    img_for_cropping = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)

    predictions = []
    for result in results:
        if result.boxes.data is not None and len(result.boxes.conf) > 0:
            for i in range(len(result.boxes.conf)):
                if result.boxes.conf[i] > confidence_threshold:
                    box = result.boxes.data[i]
                    xmin, ymin, xmax, ymax = int(box[0]), int(box[1]), int(box[2]), int(box[3])
                    x_center = (xmin + xmax) // 2
                    y_center = (ymin + ymax) // 2
                    cv2.rectangle(img, (xmin, ymin), (xmax, ymax), (0, 255, 0), 2)
                    label = result.names[int(result.boxes.cls[i])]
                    score = result.boxes.conf[i]
                    cv2.putText(img, f'{label} {score:.2f}', (xmin, ymin - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.9, (36, 255, 12), 2)
                    predictions.append(f'{label} {score:.2f}')

                    # Crop the image
                    buffer_size = 100
                    xmin_crop = max(0, xmin - buffer_size)
                    ymin_crop = max(0, ymin - buffer_size)
                    xmax_crop = min(img_for_cropping.shape[1], xmax + buffer_size)
                    ymax_crop = min(img_for_cropping.shape[0], ymax + buffer_size)
                    crop_img = img_for_cropping[ymin_crop:ymax_crop, xmin_crop:xmax_crop]
                    crop_img = cv2.cvtColor(crop_img, cv2.COLOR_RGB2BGR)
                    crop_filename = f'{filename}_x{x_center}_y{y_center}.jpg'
                    cv2.imwrite(os.path.join(cropped_dir, crop_filename), crop_img)

    # Save the original image with annotations
    h, w, _ = img.shape
    blank = 255 * np.ones(shape=[h//4, w, 3], dtype=np.uint8)
    img = cv2.vconcat([img, blank])
    cv2.putText(img, ', '.join(predictions), (10, img.shape[0]-10), cv2.FONT_HERSHEY_SIMPLEX, 0.9, (0,0,0), 2)
    output_path = os.path.join(analysed_dir, f'analysed_{filename}')
    cv2.imwrite(output_path, img)

def poll_folder():
    print("Finding people...")
    while True:
        try:
            current_files = set(os.listdir(input_folder))
            new_files = current_files - processed_files
            for file in new_files:
                if file.endswith(".jpg") or file.endswith(".png"):
                    print(f"Processing new file: {file}")
                    process_image(file)
                    processed_files.add(file)
            time.sleep(10)  # Check for new files every 10 seconds
        except Exception as e:
            print(f"Error during polling: {e}")

if __name__ == "__main__":
    print("Start")
    poll_folder()
