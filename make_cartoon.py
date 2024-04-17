from wand.image import Image
from wand.drawing import Drawing
import argparse
from os.path import exists

parser = argparse.ArgumentParser(description='Creates a balloon of text at a specified point in an image')
parser.add_argument('-i','--image',action='store',required=True, help='Source image')
parser.add_argument('-t','--text',action='store',required=True, help='Text in balloon')
args = parser.parse_args()

if not exists(args.image):
	print("No such file {0}".format(args.image))
	exit()

image1 = Image(filename=args.image)

# Scale image to 520 width
dimensions = image1.size
newheight = int((520/dimensions[0] ) * dimensions[1])
image1.resize(520, newheight)
image1.save(filename="stage_1.jpg")

# Add text
text = Drawing()
text.font = 'Verdana'
text.fill_color = '#000000'
text.font_size = 40
text.text(150,150,'OMGBARF')
text(image1)
image1.save(filename="stage_2.jpg")

# Add balloon
balloon = Drawing()
balloon.fill_color = '#FF0000'
balloon.rectangle(20,20,100,100)
balloon(image1)
image1.save(filename="stage_3.jpg")


#Add path
points = [(100,100),(200,200),(300,100)]
path = Drawing()
path.fill_color = '#00FF00'
path.stoke_color = '#000000'
path.polyline(points)
path(image1)
image1.save(filename="stage_4.jpg")

