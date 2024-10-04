import os
import sys
import threading
from queue import Queue
from multiprocessing.pool import ThreadPool as Pool
from PIL import Image
import pytesseract
from halo import Halo
from pytesseract import Output


lock = threading.Lock()

class bounding_box:
    def __init__(self, text, bounds, area):
        self.text = text
        self.bounds = bounds
        self.area = area

# worker tries to scan a single image and adds to a queue
def worker(k, filenames, spacing, images_path):
    try:
        scanner(k, filenames, spacing, images_path)
    except Exception as e:
        print("Error on slide", k, e)


def scanner(k, filenames, spacing, images_path):
    # Filter out bounding boxes with confidence > 60% and text is not empty
    saved_boxes = []
    global Headers, Images

    if k >= 10:
        filenames = filenames[:-1]
    if k >= 100:
        filenames = filenames[:-2]

    boxes = pytesseract.image_to_data(Image.open(
        images_path+"/"+filenames+str(k)+".png"), output_type=Output.DICT)
    # count all bounding boxes
    n_boxes = len(boxes['level'])
    for i in range(n_boxes):
        # Fall all bounding boxes with confidence > 60%
        if int(boxes['conf'][i]) > 60 and boxes['text'][i] != "":
            (x, y, w, h) = (boxes['left'][i], boxes['top']
                            [i], boxes['width'][i], boxes['height'][i])
            # Might need to be x+w, y+h not sure
            saved_boxes.append(bounding_box(
                boxes['text'][i], (x, y, w, h), w*h))

    # Variables to store the biggest box selection
    max_height = 0
    if len(saved_boxes) < 4:
        lock.acquire()
        Headers[k] = (("# ERROR - slide "+str(k)+"\n"))
        Images[k] = ("![](./"+images_path+"/"+filenames+str(k)+".png)\n\n")
        lock.release()
        return
    cur_height = saved_boxes[0].bounds[3]
    prev_y = -sys.maxsize - 1
    ran = ()
    start_pos = 0
    it = 0

    # for box in saved_boxes:
    #     print(box.text, box.bounds)

    # Loop to find the biggest box selection
    for box in saved_boxes:
        if prev_y > 0 and abs(box.bounds[1] - prev_y) < spacing:
            if box.bounds[3] > cur_height:
                cur_height = box.bounds[3]
        elif prev_y > 0 and abs(box.bounds[1] - prev_y) >= spacing:
            if max_height < cur_height:
                ran = (start_pos, it-1)
                max_height = cur_height
            cur_height = 0
            start_pos = it
        prev_y = box.bounds[1]
        it += 1

    # Debug print to see the biggest box selection
    # print(ran, max_height)

    # Write to lists
    lock.acquire()
    if ran != ():
        header = " ".join(
            [saved_boxes[i].text for i in range(ran[0], ran[1]+1)])
        Headers[k] = (("# "+header+"\n"))
    else:
        header = "ERROR - slide "+str(k)
        Headers[k] = (("# "+header+"\n"))
    Images[k] = ("!["+header+"](./"+images_path+"/"+filenames+str(k)+".png)\n\n")
    lock.release()


# Grab arguments from command line
images_path = sys.argv[1]
md_name = sys.argv[2]+".md"
spacing = 7
if len(sys.argv) > 3:
    spacing = int(sys.argv[3])

filenames = os.listdir(images_path)[0].split("-")[0]+"-0"

amount = len(os.listdir(images_path))+1

# Images to be written
Headers = [None] * len()
Images = [None] * len(filenames)

#TODO: probably use a mutexed list or maybe a linked list to store the writeable data


# Remove the file if it already exists
try:
    os.remove(md_name)
except OSError:
    pass

file = open(md_name, "w")

# Start spinner
spinner = Halo(text='Scanning...', spinner='dots')
spinner.start()

# Create threads list
threads = []

# https://stackoverflow.com/a/15144090
# append threads to list and start them 
for k in range(1, amount):
    threads.append(threading.Thread(target=worker, args=(k, filenames, spacing, images_path)))
    threads[-1].start()
    
# wait for all threads to finish                                            
for t in threads:
    t.join()
    
for i in range(1, amount):
    file.write(Headers[i])
    file.write(Images[i])

file.close()
spinner.stop()
print("Markdown file created successfully:", md_name+".md")


# Deprecated area code
'''
  # Variables to store the biggest box selection
    max_area = 0
    if len(saved_boxes) == 0:
        file.write(("# ERROR - slide "+str(k)+"\n"))
        file.write("![](./"+images_path+"/"+filenames+str(k)+".png)\n\n")
        continue
    cur_area = saved_boxes[0].area
    prev_y = -sys.maxsize - 1
    ran = ()
    start_pos = 0
    it = 0
    # Loop to find the biggest box selection
    for box in saved_boxes:
        if prev_y > 0 and abs(box.bounds[1] - prev_y) < 6:
            cur_area += box.area
        elif prev_y > 0 and abs(box.bounds[1] - prev_y) >= 6:
            if max_area < cur_area:
                ran = (start_pos, it-1)
                max_area = cur_area
            cur_area = 0
            start_pos = it
        prev_y = box.bounds[1]
        it += 1
'''
