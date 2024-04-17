from wand.image import Image
from wand.drawing import Drawing
import argparse
from os.path import exists
import json

parser = argparse.ArgumentParser(description='Creates a balloon of text at a specified point in an image')
parser.add_argument('-i','--image',action='store',required=True, help='Source image')
parser.add_argument('-t','--text',action='store',required=True, help='Text in balloon')
args = parser.parse_args()

if not exists(args.image):
	print("No such file {0}".format(args.image))
	exit()

image1 = Image(filename=args.image)
text_string = args.text

# Scale image to 520 width
dimensions = image1.size
new_width = 520
new_height = int((new_width/dimensions[0] ) * dimensions[1])
image1.resize(new_width, new_height)
image1.save(filename="stage_1.jpg")

balloon_fill_color = '#FEFEFE'
balloon_stroke_color = '#000000'

# Add text
text = Drawing()
text.font = 'Verdana'
text.fill_color = balloon_stroke_color
text.font_size = 20
text.gravity = 'north_west'
text.text(120,105,text_string)
metrics = text.get_font_metrics(image1,text_string)

(text_width, text_height) = metrics.size()
print("text height: {0}, text width: {1}".format(text_height, text_width))
image1.save(filename="stage_2.jpg")

# Add balloon
rectangle_height = text_height
rectangle_width = text_width + 50
balloon = Drawing()
balloon.fill_color = balloon_fill_color
balloon.stroke_color = balloon_stroke_color
balloon.rectangle(120,105, None, None, rectangle_width, rectangle_height)



#Add path
points = [(100,100),(200,200),(300,100)]
path = Drawing()
path.fill_color = balloon_fill_color
path.stoke_color = balloon_stroke_color
path.polyline(points)
image1.save(filename="stage_4.jpg")

#Assemble image
balloon(image1)
path(image1)
text(image1)
image1.save(filename="stage_3.jpg")
