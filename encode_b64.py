import base64
from io import BytesIO
import sys

from PIL import Image


if len(sys.argv) != 2:
    print("Usage: python encode_b64.py <filename>")
    sys.exit(1)


def convert_to_base64(image_path, dpi):
    with open(image_path, 'rb') as f:
        img = Image.open(f)
        
        img_buffer = BytesIO()
        img.save(img_buffer, format='PNG', dpi=(dpi, dpi), transparent=1)
        encoded_image = base64.b64encode(img_buffer.getvalue()).decode('utf-8')
        return encoded_image

        
# with open(sys.argv[1], 'rb') as f:
#     encoded_image = base64.b64encode(f.read()).decode('utf-8')
# 
encoded_image = convert_to_base64(sys.argv[1], dpi=600)

# Write the encoded string to a text file
with open('output.txt', 'w') as f:
    f.write(encoded_image)

