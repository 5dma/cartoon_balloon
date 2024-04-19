from wand.image import Image
from wand.drawing import Drawing
from wand.color import Color
from os.path import exists
import json
import numpy

NEW_WIDTH = 520
BALLOON_FILL_COLOR = Color('#f2e38b')
BALLOON_STROKE_COLOR = Color('#000000')
EXCESS_FONT_HEIGHT = 10
PADDING = 10
EXCESS_TEXT_HEIGHT = 10
ELEVATION = 10
CALLOUT_INDENT = 10
CALLOUT_SPACE = 20
ELEVATION = 5
INDENT = 10
SPACE = 20
STROKE_WIDTH = 2
EXTRA_OFFSET = 10
FONT_SIZE = 20
NEW_IMAGE = '/tmp/new_image.jpg'

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
debug = data['debug']

# Scale image to 520 width
dimensions = new_image.size
new_height = int((NEW_WIDTH/dimensions[0] ) * dimensions[1])
new_image.resize(NEW_WIDTH, new_height)
number_text_lines = text_string.count('\n') + 1
is_multiline = (number_text_lines > 1)

if debug:
	print("Original size (wxh): {0}, {1}".format(dimensions[0], dimensions[1]))
	print("Scaled size (wxh): {0}, {1}".format(NEW_WIDTH, new_height))
	print("Is this a multiline text string? {0}".format(is_multiline))


# Add text
text = Drawing()
text.font = 'Verdana'
text.fill_color = BALLOON_STROKE_COLOR
text.font_size = FONT_SIZE
text.gravity = 'north_west'
metrics = text.get_font_metrics(new_image,text_string,multiline=is_multiline)
float_metrics = metrics.size()
text_width = int(float_metrics[0])
text_height = int(float_metrics[1])

if debug:
	print(metrics)
	print("text height: {0}, text width: {1}".format(text_height, text_width))

left_offset = data['text_bottom_left'][0]

excess_spacing = text_height - (number_text_lines * text.font_size) # text height - characters
partial_excess_spacing = excess_spacing * 0.75 # account for 0.75 for adjusting the top.
baseline = int(data['text_bottom_left'][1] - (number_text_lines * text.font_size) -partial_excess_spacing)
offset = 0
if baseline < 0:
	offset = abs(baseline) + EXTRA_OFFSET
	print("Found a text baseline of {0}, so increasing height of image by {1} to {2}".format(baseline,offset, new_height + offset))
	new_image.extent(None,new_height + offset ,None,None, 'south')

if debug:
	print("left_offset: {0}, baseline: {1}, offset: {2}".format(left_offset, baseline, offset))

text.text(left_offset, baseline + offset, text_string)


# Add balloon
balloon = Drawing()
balloon.stroke_width = STROKE_WIDTH
balloon.stroke_color = BALLOON_STROKE_COLOR
balloon.fill_color = BALLOON_FILL_COLOR
left = data['text_bottom_left'][0] - PADDING
top = data['text_bottom_left'][1] - text_height + EXCESS_TEXT_HEIGHT - PADDING + offset
right = left + text_width + 2*PADDING
bottom = top + text_height - EXCESS_TEXT_HEIGHT + 2*PADDING
balloon.rectangle(left, top, right,bottom)


#Add path
vertex = data['callout_vertex']
vertex[1] = vertex[1] + offset
p1 = (left + INDENT, bottom - ELEVATION)
p2 = vertex
p3 = (p1[0] + SPACE, p1[1])
path = Drawing()
path.stroke_width = STROKE_WIDTH
path.stroke_color = BALLOON_STROKE_COLOR
path.fill_color = BALLOON_FILL_COLOR
 
# points list for polygon
points = [p1, p2, p3]

if debug:
	print("Path points: {0}".format(points))
 
# draw polyline using polyline() function
path.polyline(points)


#Assemble image
balloon(new_image)
path(new_image)
text(new_image)
new_image.save(filename=NEW_IMAGE)
print("New image at {0}".format(NEW_IMAGE))
