import cv2
import numpy as np

# Load the image
image = cv2.imread('2.jpg')
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

# Create a mask from the dilated edges
mask = cv2.merge([dilated_edges, dilated_edges, dilated_edges])  # Convert to 3-channel mask

# Apply the mask to the resized image
result = cv2.bitwise_and(resized_image, mask)

# Create a white background
white_background = np.full_like(resized_image, 255)

# Combine the result with the white background
final_result = cv2.add(result, cv2.bitwise_not(mask, white_background))

# Save the final result
cv2.imwrite('output.png', final_result)

# Display the final result
cv2.imshow("Final Result", final_result)
cv2.waitKey(0)
cv2.destroyAllWindows()