# Image retrieval
GASearcher (where GAS stands for "Generic Annotation System") is a Django-based software that allows users to search in
an image database using a text query. System show the results alongside their predefined classes, which
are intended to assist users in selecting suitable word combinations for formulating queries that more likely describe
the desired image.

Main features:
* text-based search
* similarity search based on a selected image from the currently displayed images
* logging the search progress of individual users 
* changing the experiment settings within the framework of changing the collections of images used
* possibility of preprocessing own video dataset and using it by searcher
* evaluation of logs and creation of plots from result

Text queries to the database and classification is implemented using
[the CLIP neural network](https://beta.openai.com/).

## Project structure
The GASearcher web application project is located in [gasearcher folder](gasearcher) with a description of its functionality 
and with instruction for build of searcher.

Helper code for processing images and their classification is included in [the src folder](src). The folder contains
[code](src/parse_video.py) for processing videos into individual frames, [classification](src/top_classes.py) of frames
into classes, and [code](src/images_to_clip.py) for obtaining feature of frames from the CLIP. For preprocessing
whole dataset at once can be used [class `Preprocessor`](src/preprocessor.py) and for evaluation and creation of plots
can be used [class `Evaluator`](src/evaluator.py).

The current version of the work associated with this software is available
at [this link](https://www.overleaf.com/read/ffjzxjyhtznc). Software documentation is available in
[the docs](docs) folder within information about reusing software with different dataset.
It is important to note that this is a prototype that was used for experimental purposes in mention work.

## Dictionaries
Currently, project includes two dictionaries of classes:

1. [dictionary](nounlists/nounlist.txt) - containing exactly 6,771 most common english nouns.

2. [dictionary](nounlists/sea_nounlist.txt) - containing 512 names of sea creatures and other things found in the sea.

These two dictionaries can be use for preprocessing of new dataset.