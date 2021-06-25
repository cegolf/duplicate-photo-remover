from pathlib import WindowsPath
import imageio
from PIL import Image
from PIL.ExifTags import TAGS
import os
import datetime
import shutil
from itertools import combinations
import config as cfg

directory = cfg.info["directory"]
matches = 0


class ImageObj:
    fileType =""
    shape =""
    height=""
    width =""
    dimension=""
    size =""
    maxRGB=""
    minRGB=""
    rChannel=""
    gChannel=""
    bChannel=""
    dup=[]

    def __init__(self, fileType, path):
        self.fileType = fileType 
        self.path = path 

def getExifdata(image, obj):
    exifdata = image.getexif()
    # iterating over all EXIF data fields
    for tag_id in exifdata:
        # get the tag name, instead of human unreadable tag id
        tag = TAGS.get(tag_id, tag_id)
        data = exifdata.get(tag_id)
        # decode bytes 
        if isinstance(data, bytes):
            data = data.decode()
        # print(f"{tag:25}: {data}")
        setattr(obj, tag, data)


def setImageProps(im, pic):
    im.shape = pic.shape

    im.height = pic.shape[0]

    im.width = pic.shape[1]

    im.dimension = pic.ndim

    im.size = pic.size

    im.maxRGB = pic.max()

    im.minRGB = pic.min()

    im.rChannel = pic[100,50,0]

    im.gChannel = pic[ 100, 50, 1]

    im.bChannel = pic[ 100, 50, 2]

def compateDates(image1, image2):
    date1 = getattr(image1, 'DateTime')
    date2 = getattr(image2, 'DateTime')
    
    date1NumList = []
    date2NumList = []
    for half in date1.split():
        date1NumList.extend(half.split(':'))
    for half in date2.split():
        date2NumList.extend(half.split(':'))

    datetime1 = datetime.datetime(int(date1NumList[0]), int(date1NumList[1]),int(date1NumList[2]),int(date1NumList[3]),int(date1NumList[4]),int(date1NumList[5]))
    datetime2 = datetime.datetime(int(date2NumList[0]), int(date2NumList[1]),int(date2NumList[2]),int(date2NumList[3]),int(date2NumList[4]),int(date2NumList[5]))
    # print(datetime1.timestamp())
    diff = abs(datetime1.timestamp() - datetime2.timestamp())
    # Will return true if the difference is less than 10 seconds apart
    return diff < 10 



def compareGPS(image1,image2):
    gps1 = getattr(image1, 'GPSInfo')
    gps2 = getattr(image2, 'GPSInfo')
    print(str(gps1) + str(image1))
    print(str(gps2) + str(image2))

def compareSize(image1, image2):
    size1 = getattr(image1, 'size')
    size2 = getattr(image2, 'size')
    diff = abs(size1) - abs(size2)
    percentdiff = (abs(diff) / abs(size1)) * 100
    return percentdiff < 5

def compareHeight(image1, image2):
    height1 = getattr(image1, 'height')
    height2 = getattr(image2, 'height')
    diff = abs(height1) - abs(height2)
    percentdiff = (abs(diff) / abs(height1)) * 100
    return percentdiff < 5

def compareWidth(image1, image2):
    width1 = getattr(image1, 'width')
    width2 = getattr(image2, 'width')
    diff = abs(width1) - abs(width2)
    percentdiff = (abs(diff) / abs(width1)) * 100
    return percentdiff < 5

def compareXResolution(image1,image2):
    xres1 = getattr(image1, "XResolution")
    xres2 = getattr(image2, "XResolution")
    diff = abs(xres1) - abs(xres2)
    percentDiff = (abs(diff) / abs(xres1)) * 100
    return percentDiff < 2

def compareYResolution(image1,image2):
    yres1 = getattr(image1, "YResolution")
    yres2 = getattr(image2, "YResolution")
    diff = abs(yres1) - abs(yres2)
    percentDiff = (abs(diff) / abs(yres1)) * 100
    return percentDiff < 2

def compareWhitePoint(image1,image2):
    wp1 = getattr(image1, "WhitePoint")
    wp2 = getattr(image2, "WhitePoint")
    return wp1 == wp2

def compareImages(image1, image2):
    match = False
    ifHeightSame = compareHeight(image1, image2)
    ifWidthSame  = compareWidth(image1, image2)
    ifSizeSame   = compareSize(image1,image2) # this is file size not image h x w
    ifAtSameTime = compateDates(image1,image2)
    ifSameXRes = compareXResolution(image1, image2)
    ifSameYRes = compareXResolution(image1, image2)
    ifSameWhitePoint = compareWhitePoint(image1,image2)

    if(ifHeightSame and ifSizeSame and ifWidthSame and ifAtSameTime and ifSameXRes and ifSameYRes and ifSameWhitePoint):
        match = True
        
    return match
def scanImages(images):
	sift = cv.SIFT_create()

	for image in images:
		image['keypoints'], image['descriptors'] = sift.detectAndCompute(image['image'], None)

	return imgs

def iterateDirectory(directory):
	imgs = []
	for file in os.listdir(directory):
		if(file.lower().endswith(('.jpg','.jpeg', '.JPG', '.PNG','.gif','.png'))):
			path = os.path.join(directory, file)
			imgs.append({
				'image': cv.imread(path, cv.IMREAD_GRAYSCALE),
				'path': path
			})

	return imgs

    ########################################
    # DO NOT DELETE. These are the keys/attributes that can be compared between each photo
    # print(im1.__dict__.keys())
    # dict_keys(['fileType', 'GPSInfo', 'ResolutionUnit', 'ExifOffset', 'Make', 'Model', 'YCbCrCoefficients', 'Orientation', 'DateTime', 'YCbCrPositioning', 'YResolution', 'Copyright', 'XResolution', 'Artist', 'WhitePoint', 'PrimaryChromaticities', 'shape', 'height', 'width', 'dimension', 'size', 'maxRGB', 'minRGB', 'rChannel', 'gChannel', 'bChannel'])
    ############################################
                        
                     

print("Starting Search...")
print("Directory: ", directory)
imageList = iterateDirectory(directory)

imageCount = len(imageList)

print(imageList[0].__dict__.keys())

# for comb in combinations(imageList,2):
#     match = compareImages(comb[0], comb[1])
#     print(match)
#     if(match):
#         print("MATCH FOUND")
#         #first image is comb[0]
#         #second is image comb[0]

#         comb[0].dup.append(comb[1].path)
#         comb[1].dup.append(comb[0].path)


#         im1str = str(comb[0]).split('at ')[1].replace('>', '')
#         im2str = str(comb[1]).split('at ')[1].replace('>', '')
for img in imageList:
    print(img.dup)
       
