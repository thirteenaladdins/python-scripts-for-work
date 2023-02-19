# Import the required modules
import sys
from PyPDF2 import PdfReader, PdfWriter
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from reportlab.lib.utils import ImageReader 
import io

import base64

# Check if a pdf file is provided as an argument
if len(sys.argv) < 2:
    print("Please provide a pdf file as an argument.")
    sys.exit(1)

# Get the input pdf file name
input_file = sys.argv[1]

# Create a PdfFileReader object to read the input file
try:
    reader = PdfReader(input_file)
except Exception as e:
    print(f"Error: {e}")
    sys.exit(1)

# Create a PdfFileWriter object to write the output file
writer = PdfWriter()

# input image file, then convert, then import into this script?
try:
    with open('output.txt', 'r') as f:
        encoded_image_data = f.read()
        # add prefix to image
        encoded_image_data = 'data:image/png;base64,' + encoded_image_data
except Exception as e:
    print(f"Error: {e}")
    sys.exit(1)
    
def draw_image(canvas, image_data, x, y, width=None, height=None):
    decoded_image_data = base64.b64decode(image_data.split(',')[1])
    image_reader = ImageReader(io.BytesIO(decoded_image_data))
    img_width, img_height = image_reader.getSize()
    aspect_ratio = img_width / img_height

    if width is not None and height is not None:
        if width / height > aspect_ratio:
            width = height * aspect_ratio
            print(width)
        else:
            height = width / aspect_ratio
            print(height)
    
    center_x = page_width / 2

    # Calculate the position to place the image to center it on the page
    x = center_x - (width / 2)
    
    canvas.drawImage(ImageReader(image_reader), x, y - 130, width=width, height=height, mask='auto')


# Define the footer and header text
# TODO: add standard footer
footer_text = "This is a footer"
# header_text = "This is a header"

# Loop through each page of the input file
for page_num in range(len(reader.pages)):
    # Get the current page
    page = reader.pages[page_num]

    # Create a canvas object to draw the footer and header
    canvas_obj = canvas.Canvas("temp.pdf", pagesize=A4)

    # Get the page width and height
    page_width, page_height = A4
    
    # Draw the footer text at the bottom center of the page
    canvas_obj.setFont("Helvetica", 12)
    canvas_obj.drawCentredString(page_width / 2, 30, footer_text)

    # draw_image(canvas_obj, encoded_image_data, page_width / 2, page_height)

    # page_width and page_height are being passed in here
    draw_image(canvas_obj, encoded_image_data, page_width, page_height, 220, 180)
    
    # Save the canvas object
    canvas_obj.save()

    # Merge the canvas object with the current page
    watermark = PdfReader("temp.pdf")
    page.merge_page(watermark.pages[0])

    # Add the modified page to the output file
    writer.add_page(page)

# Create the output file name
# Create the output file name
output_file = input_file[:-4] + "_modified.pdf"

try:
    # Write the output file
    with open(output_file, "wb") as out:
        writer.write(out)

    # Print a success message
    print(f"Successfully created {output_file} with added footer and header.")
except Exception as e:
    # Print an error message if an exception occurs
    print(f"Error occurred while creating {output_file}: {str(e)}")

