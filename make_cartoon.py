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
SPACE = 10
STROKE_WIDTH = 2
EXTRA_OFFSET = 10
FONT_SIZE = 20
NEW_IMAGE = '/tmp/new_image.jpg'


def drawing_with_split_text(temp_image, left_offset, start_text):

	max_width = NEW_WIDTH - left_offset - PADDING - STROKE_WIDTH
	is_multiline = False

	text = Drawing()
	text.font = 'Verdana'
	text.fill_color = BALLOON_STROKE_COLOR
	text.font_size = FONT_SIZE
	text.gravity = 'north_west'

	word_list = start_text.split(' ')
	current_word = word_list.pop(0)
	current_text = current_word
	while word_list:
		#print(current_text)
		metrics = text.get_font_metrics(temp_image,current_text,multiline=is_multiline)
		text_width = metrics[4]
		if text_width > max_width:
			old_text = current_text.rsplit(' ', 1)
			new_text = '\n'.join(old_text)
			current_text = new_text
			is_multiline = True
		current_word = word_list.pop(0)
		current_text = current_text + ' ' + current_word

	metrics = text.get_font_metrics(temp_image,current_text,multiline=is_multiline)
	number_text_lines = current_text.count('\n') + 1
	if debug:
		print("At end of drawing_with_split_text:")
		print("  new_text:" + new_text)
		print("  text width: {0}".format(metrics[4]))

	return {'text_drawing': text, 'split_string': current_text, 'metrics': metrics, 'number_text_lines': number_text_lines  } 


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
resize_proportions = {}
dimensions = new_image.size
new_height = int((NEW_WIDTH/dimensions[0] ) * dimensions[1])
new_image.resize(NEW_WIDTH, new_height)
resize_proportions['x'] =  NEW_WIDTH/dimensions[0]
resize_proportions['y'] =  new_height/dimensions[1]

if debug:
	print("Original size (wxh): {0}, {1}".format(dimensions[0], dimensions[1]))
	print("Scaled size (wxh): {0}, {1}".format(NEW_WIDTH, new_height))


# Add text
left_offset = int(data['text_bottom_left'][0] * resize_proportions['x'])
text_analysis =  drawing_with_split_text(new_image, left_offset, data['text_string'])
metrics = text_analysis['metrics']
text_height = metrics[5]
text_width = metrics[4]
text_drawing = text_analysis['text_drawing']
font_size = metrics[0]
excess_spacing = text_height - (text_analysis['number_text_lines'] * font_size) # text height - characters
partial_excess_spacing = excess_spacing * 0.75 # account for 0.75 for adjusting the top.
baseline = int((data['text_bottom_left'][1] * resize_proportions['y']) - (text_analysis['number_text_lines'] * font_size) - partial_excess_spacing)

if debug:
	print(text_analysis['metrics'])
	print("text width: {0}, text height: {1}".format(metrics[4],metrics[5] ))
	print("Is this a multiline text string? {0}".format(text_analysis['number_text_lines'] > 1))
	print("Number of text lines: {0}".format(text_analysis['number_text_lines']))
	print("Font size: {0}".format(font_size))
	print("Excess_spacing: {0}".format(excess_spacing))
	print("Partial excess spacing: {0}".format(partial_excess_spacing))
	print("Baseline: {0}".format(baseline))


offset = 0
if baseline < 0:
	offset = abs(baseline) + EXTRA_OFFSET
	print("Found a text baseline of {0}, so increasing height of image by {1} to {2}".format(baseline,offset, new_height + offset))
	new_image.extent(None,new_height + offset ,None,None, 'south')

if debug:
	print("left_offset: {0}, baseline: {1}, offset: {2}".format(left_offset, baseline, offset))

text_drawing.text(left_offset, baseline + offset, text_analysis['split_string'])


# Add balloon
balloon = Drawing()
balloon.stroke_width = STROKE_WIDTH
balloon.stroke_color = BALLOON_STROKE_COLOR
balloon.fill_color = BALLOON_FILL_COLOR
left = int(data['text_bottom_left'][0] * resize_proportions['x']) - PADDING
top = int(data['text_bottom_left'][1] * resize_proportions['y']) - text_height + EXCESS_TEXT_HEIGHT - PADDING + offset
right = left + text_width + 2*PADDING
bottom = top + text_height - EXCESS_TEXT_HEIGHT + 2*PADDING
balloon.rectangle(left, top, right,bottom)
if debug:
	print("left: {0}, top: {1}, right: {2}, bottom: {3}".format(left,top,right,bottom))


#Add path
original_vertex = data['callout_vertex']
vertex = [None, None ]
vertex[0] = int(resize_proportions['x'] * original_vertex[0])
vertex[1] = int(resize_proportions['y'] * original_vertex[1])
vertex[1] = vertex[1] + offset
balloon_midpoint = int((right - left)/2 + left)
p1 = (balloon_midpoint - SPACE, bottom - ELEVATION)
p2 = vertex
p3 = (balloon_midpoint + SPACE, bottom - ELEVATION)
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
text_drawing(new_image)
new_image.save(filename=NEW_IMAGE)
print("New image at {0}".format(NEW_IMAGE))
