from gas.data import LoaderDatabase
from gas.logger import Logger
from gas.searcher import Searcher
from gas.settings import SEA_DATABASE, COMBINATION, PATH_DATA, SUR, SHOWING

loader = LoaderDatabase(PATH_DATA, SEA_DATABASE)
class_data = loader.get_photos_classes()
classes, class_pr = loader.get_classes()

size_dataset = len(class_data)
targets = loader.set_finding(size_dataset)

# the initial set of images indexes to be shown in the search result
first_show = loader.load_first_screen(class_data, size_dataset, targets)

searcher = Searcher(loader.get_clip_data(), COMBINATION,
                    Logger(PATH_DATA, loader.get_context(size_dataset, SUR), targets, SEA_DATABASE), SHOWING)
