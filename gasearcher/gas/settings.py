import os
from gasearcher.settings import STATICFILES_DIRS

# configuration
SEA_DATABASE = False
COMBINATION = False  # if result should be combined with previous result
USING_SOM = True
PATH_DATA = os.path.join(STATICFILES_DIRS[0], "data/")  # get path to data
SUR = 5  # surrounding of image in context
IMAGES_ON_LINE = 12
LINES = 5
SHOWING = IMAGES_ON_LINE * LINES  # number of shown image in result
NUMBER_OF_SEARCHED = 5

PATH_CLIP = "clip" # name of folder with preprocessed CLIP data
PATH_NOUNLIST = "nounlist.txt" # name of the nounlist
PATH_CLASSES = "result.csv" # name of the file with classification of images
PATH_SELECTION = "" # name of the file with indexes of images which should be used for searching (can be empty)
PATH_ENDS = "videos_end.txt" # name of the file with indexes of images which represents ends of each video
PATH_LOG = "log.csv" # name of the log file for text queries
PATH_LOG_SIMILARITY = "log_similarity.csv" # name of the log file for image queries