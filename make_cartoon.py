from wand.image import Image
from wand.drawing import Drawing
from os.path import exists
import json

NEW_WIDTH = 520
BALLOON_FILL_COLOR = '#FEFEFE'
BALLOON_STROKE_COLOR = '#000000'
EXCESS_FONT_HEIGHT = 10
PADDING = 10
EXCESS_TEXT_HEIGHT = 10
ELEVATION = 10
CALLOUT_INDENT = 10
CALLOUT_SPACE = 20


if not exists('points.json'):
	print("The configuration file points.json is missing. Create it and rerun this script.")
	exit()


infile = open('points.json','r')
data = json.load(infile)
infile.close()
#print(data)


if not exists(data['source_image']):
	print("The source image {0} is missing. Try again.".format(data['source_image']))
	exit()

new_image = Image(filename = data['source_image'])
text_string = data['text_string']

# Scale image to 520 width
dimensions = new_image.size
new_height = int((NEW_WIDTH/dimensions[0] ) * dimensions[1])
new_image.resize(NEW_WIDTH, new_height)


# Add text
text = Drawing()
text.font = 'Verdana'
text.fill_color = BALLOON_STROKE_COLOR
text.font_size = 20
text.gravity = 'north_west'
text.text(data['text_bottom_left'][0],data['text_bottom_left'][1] - EXCESS_FONT_HEIGHT * 2,text_string)
metrics = text.get_font_metrics(new_image,text_string)
(text_width, text_height) = metrics.size()

print(metrics)
print("text height: {0}, text width: {1}".format(text_height, text_width))

# Add balloon
balloon = Drawing()
balloon.fill_color = BALLOON_FILL_COLOR
balloon.stroke_color = BALLOON_STROKE_COLOR
left = data['text_bottom_left'][0] - PADDING
top = data['text_bottom_left'][1] - text_height + EXCESS_TEXT_HEIGHT - PADDING
right = left + text_width + 2*PADDING
bottom = top + text_height - EXCESS_TEXT_HEIGHT + 2*PADDING
balloon.rectangle(left, top, right,bottom)


#Add path
points = [(100,100),(150,100),(75,75)]
path = Drawing()
path.fill_color = BALLOON_FILL_COLOR
path.stoke_color = BALLOON_STROKE_COLOR
path.polyline(points)

#Assemble image
balloon(new_image)
path(new_image)
text(new_image)
new_image.save(filename="stage_3.jpg")
