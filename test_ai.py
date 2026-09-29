import cv2
from ultralytics import YOLO

print("Loading AI Model...")
# Load the smallest, fastest YOLOv8 model
model = YOLO('yolov8n.pt') 

print("Turning on laptop webcam...")
# 0 refers to your laptop's built-in webcam
cap = cv2.VideoCapture(0)

if not cap.isOpened():
    print("Error: Could not open webcam.")
    exit()

print("AI is running! Press 'q' on your keyboard to close the window.")

while True:
    # Capture the video frame-by-frame
    success, frame = cap.read()
    
    if success:
        # Give the frame to the AI to find objects (people, chairs, etc.)
        results = model(frame)
        
        # Draw the red bounding boxes on the picture
        annotated_frame = results[0].plot()
        
        # Show the picture in a popup window
        cv2.imshow("Live AI Vision Test - Press 'q' to quit", annotated_frame)
        
        # If the user presses the 'q' key, stop the loop
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break
    else:
        break

# Turn off the camera and close the window safely
cap.release()
cv2.destroyAllWindows()