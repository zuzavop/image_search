# GASearcher documentation
## Project structure
The GASearcher project has the following structure:

* gas/: The main application directory.
  * data.py: Loads data processed by the CLIP neural network.
  * logger.py: Writes search results to the log.
  * models.py: Starts loading data and creating objects (Logger and Searcher) necessary for searching.
  * searcher.py: Processes a search in the currently used dataset.
  * settings.py: Define basic settings of the searcher.
  * views.py: Handles user requests and send the search results to templates.
  * urls.py: Maps URLs to views.
  
* templates/: HTML templates for the user interface.
* translations/: Defined translations of phrases used in the searcher.
* static/: Static files such as CSS and JavaScript and used dataset with its preprocessed data.
* start_server: Shell script to start the Django development server on Linux.
* start_server.bat: Batch script to start the Django development server on Windows.
* requirements.txt: A list of required Python packages.

## Used libraries
GASearcher uses the following additional python libraries:

* Django Debug Toolbar: A panel that displays various debug information when running Django applications. 
* ftfy
* NumPy
* Pandas: A library for data analysis and manipulation. 
* regex
* sklearn_som: A self-organizing map library. 
* tqdm
* Torch
* torchaudio
* torchvision
