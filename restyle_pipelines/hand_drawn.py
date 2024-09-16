import sys
import os
import requests
from PIL import Image, ImageFilter

# Function to call the DeepAI Image Editor API
def call_deepai_image_editor_api(image_path, text_path, api_key):
    """
    Sends the image and description text to the DeepAI image-editor API.
    """
    url = "https://api.deepai.org/api/image-editor"
    
    try:
        with open(image_path, 'rb') as img_file, open(text_path, 'rb') as text_file:
            response = requests.post(
                url,
                files={
                    'image': img_file,
                    'text': text_file,
                },
                headers={'api-key': api_key}
            )
        result = response.json()
        
        # Check if the request was successful and return the output URL
        if 'output_url' in result:
            print(f"DeepAI processed image URL: {result['output_url']}")
            return result['output_url']
        else:
            print(f"DeepAI API error: {result}")
            return None
    except Exception as e:
        print(f"Error calling DeepAI API: {e}")
        return None

# Function to download the image from a URL
def download_image(image_url, save_path):
    """
    Downloads the image from the given URL and saves it to the specified path.
    """
    try:
        response = requests.get(image_url)
        if response.status_code == 200:
            with open(save_path, 'wb') as file:
                file.write(response.content)
            print(f"Image downloaded and saved to: {save_path}")
            return save_path
        else:
            print(f"Failed to download image. Status code: {response.status_code}")
            return None
    except Exception as e:
        print(f"Error downloading image: {e}")
        return None

# Function to apply hand-drawn effect using Pillow
def apply_hand_drawn_effect(image_path):
    """
    Applies a hand-drawn effect to the image using Pillow.
    """
    try:
        # Open the image using Pillow
        img = Image.open(image_path)

        # Step 1: Apply a contour filter to simulate hand-drawn outlines
        hand_drawn_img = img.filter(ImageFilter.CONTOUR)

        # Step 2: Apply a detail enhancement filter to add more texture
        hand_drawn_img = hand_drawn_img.filter(ImageFilter.DETAIL)

        # Create the output file path
        base, ext = os.path.splitext(image_path)
        output_image_path = f"{base}_hand_drawn{ext}"

        # Step 3: Save the transformed image
        hand_drawn_img.save(output_image_path)
        print(f"Hand-drawn effect applied. Image saved to: {output_image_path}")
        return output_image_path
    except Exception as e:
        print(f"Error applying hand-drawn effect: {e}")
        return None

# Main function to execute the complete process
def main(image_path, text_path, api_key):
    # Step 1: Call the DeepAI API with the image and description file
    processed_image_url = call_deepai_image_editor_api(image_path, text_path, api_key)

    if processed_image_url:
        # Step 2: Download the processed image from the DeepAI API
        downloaded_image_path = os.path.join(os.getcwd(), 'processed_image.jpg')
        downloaded_image_path = download_image(processed_image_url, downloaded_image_path)

        if downloaded_image_path:
            # Step 3: Apply the hand-drawn effect using Pillow
            final_image_path = apply_hand_drawn_effect(downloaded_image_path)
            if final_image_path:
                print(f"Final image with hand-drawn effect saved at: {final_image_path}")

if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Usage: python hand_drawn.py <image_path> <text_path>")
    else:
        image_path = sys.argv[1]
        text_path = sys.argv[2]
        api_key = 'your_api_key_here'  # Replace with your DeepAI API key
        main(image_path, text_path, api_key)
