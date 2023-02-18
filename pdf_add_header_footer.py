# Import the required modules
import sys
from PyPDF2 import PdfReader, PdfWriter
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter, A4
from PIL import Image
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
reader = PdfReader(input_file)

# Create a PdfFileWriter object to write the output file
writer = PdfWriter()

with open('output.txt', 'r') as f:
    encoded_image_data = f.read()
    # add prefix to image
    encoded_image_data = 'data:image/png;base64,' + encoded_image_data

# with open('svgviewer-output.svg', 'rb') as f:
#     svg_data = f.read()    
    
# def draw_image_2(canvas, image_data, x, y):
#     # def draw_image(canvas, image_data, x, y, width, height):
#     decoded_image_data = base64.b64decode(image_data.split(',')[1])
#     image_reader = ImageReader(io.BytesIO(decoded_image_data))
#     # img_width, img_height = image.size

#     img_width, img_height = image_reader.getSize()

#     # Draw the image on the PDF page with the same size as it is encoded
#     canvas.drawImage(ImageReader(image_reader), x / 2, y - img_height - 24, width=img_width, height=img_height, mask='auto')
#     # canvas.drawImage(image_reader, x, y, width=width, height=height, preserveAspectRatio=True)

def draw_image(canvas, image_data, x, y, width=None, height=None):
    decoded_image_data = base64.b64decode(image_data.split(',')[1])
    image_reader = ImageReader(io.BytesIO(decoded_image_data))
    img_width, img_height = image_reader.getSize()
    aspect_ratio = img_width / img_height
    if width is not None and height is not None:
        if width / height > aspect_ratio:
            width = height * aspect_ratio
        else:
            height = width / aspect_ratio
    canvas.drawImage(ImageReader(image_reader), x / 2, y - 142, 
    width=img_width / 2.2, height=img_height / 2.2, mask='auto')

# Define the footer and header text
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
    draw_image(canvas_obj, encoded_image_data, page_width / 2, page_height)
    
    # Save the canvas object
    canvas_obj.save()

    # Merge the canvas object with the current page
    watermark = PdfReader("temp.pdf")
    page.merge_page(watermark.pages[0])

    # Add the modified page to the output file
    writer.add_page(page)

# Create the output file name
output_file = input_file[:-4] + "_modified.pdf"

# Write the output file
with open(output_file, "wb") as out:
    writer.write(out)

# Print a success message
print(f"Successfully created {output_file} with added footer and header.")