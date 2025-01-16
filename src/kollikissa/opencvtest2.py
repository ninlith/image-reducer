import cv2
import numpy as np

# Load the image
image = cv2.imread('1.jpg')
if image is None:
    print("Error: Could not load image.")
    exit()

# Resize the image to 1200x1600
resized_image = cv2.resize(image, (1200, 1600))

# Convert the resized image to grayscale
gray = cv2.cvtColor(resized_image, cv2.COLOR_BGR2GRAY)

# Detect edges using Canny edge detection
edges = cv2.Canny(gray, threshold1=50, threshold2=150)

# Dilate the edges to create a 10-pixel border around them
kernel = np.ones((10, 10), np.uint8)  # Adjust kernel size for border thickness
dilated_edges = cv2.dilate(edges, kernel, iterations=1)

# Apply Gaussian blur to the dilated edges to smooth the mask
blurred_mask = cv2.GaussianBlur(dilated_edges.astype(np.float32), (21, 21), 0)  # Blur the mask

# Normalize the blurred mask to the range [0, 1]
blurred_mask = blurred_mask / 255.0

# Convert the mask to 3 channels
blurred_mask = cv2.merge([blurred_mask, blurred_mask, blurred_mask])

# Ensure the resized image is in float32 for multiplication
resized_image_float = resized_image.astype(np.float32)

# Multiply the image with the blurred mask
result = cv2.multiply(resized_image_float, blurred_mask, dtype=cv2.CV_32F)

# Create a white background
white_background = np.full_like(resized_image_float, 255, dtype=np.float32)

# Combine the result with the white background
final_result = cv2.addWeighted(result, 1, cv2.multiply(white_background, 1 - blurred_mask, dtype=cv2.CV_32F), 1, 0)

# Convert the final result back to uint8
final_result = final_result.astype(np.uint8)

# Save the final result
cv2.imwrite('output1.jpg', final_result)

# Display the final result
cv2.imshow("Final Result", final_result)
cv2.waitKey(0)
cv2.destroyAllWindows()