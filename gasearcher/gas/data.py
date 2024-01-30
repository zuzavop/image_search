import os
import random
from ast import literal_eval

import numpy as np
import pandas as pd
import torch as torch
from sklearn_som.som import SOM

from gas.settings import PATH_CLIP, PATH_NOUNLIST, PATH_CLASSES, PATH_SELECTION, PATH_ENDS, IMAGES_ON_LINE, \
    LINES, NUMBER_OF_SEARCHED


class LoaderDatabase:
    """
    LoaderDatabase loads the data from a given database.

    Attributes:
        path_data (str): The path to the database.
        is_sea_database (bool): A boolean representing whether the database is a sea database or not.
        path_clip (str): The path to folder with preprocessed CLIP data.
        path_nounlist (str): The path to the nounlist.
        path_classes (str): The path to the file with classification of images.
        path_selection (str): The path to the file with indexes of images which should be used for searching.
        path_ends (str): The path to the file with indexes of images which represents ends of each video.
    """

    def __init__(self, path_data, is_sea_database=False):
        """
        Args:
            path_data (str): The path to the database.
            is_sea_database (bool): A boolean representing whether the database is a sea database or not.
        """
        self.path_clip = path_data + ("sea_clip" if is_sea_database else PATH_CLIP)
        self.path_nounlist = path_data + ("sea_nounlist.txt" if is_sea_database else PATH_NOUNLIST)
        self.path_classes = path_data + ("sea_result.csv" if is_sea_database else PATH_CLASSES)
        self.path_selection = path_data + ("sea_selection.txt" if is_sea_database else PATH_SELECTION)
        self.path_ends = path_data + ("sea_videos.txt" if is_sea_database else PATH_ENDS)
        self.is_sea_database = is_sea_database
        self.path_data = path_data

    def get_clip_data(self):
        """
        Loads the preprocessed data from CLIP.

        Returns:
            list: A list of preprocessed data from CLIP.

        """
        print('loading data...')
        clip_data = []

        # preprocessed data from clip
        for fn in sorted(os.listdir(self.path_clip)):
            clip_data.append(torch.load(self.path_clip + f"/{fn}"))
        return clip_data

    def get_photos_classes(self):
        """
        Loads the photo classes.

        Returns:
            dict: A dictionary where keys are integers representing image indexes
            and values are lists of indexes representing classes.

        """
        class_data = pd.read_csv(self.path_classes, sep=';').set_index('id').to_dict()['top']
        return {int(key) - 1: literal_eval(value) for key, value in class_data.items()}

    def get_classes(self):
        """
        Loads classes (names) and class probabilities.

        Returns:
            tuple: A tuple containing two lists. The first list contains class names
            and the second list contains the probability of each class.

        """
        classes = []
        class_pr = {}
        with open(self.path_nounlist, 'r') as f:
            for line in f:
                split = line.split(":")
                classes.append(split[0][:-1])
                class_pr[len(classes) - 1] = float(split[1][:-1])

        return classes, class_pr

    def get_context(self, size_dataset, sur):
        """
        Load context of each image from dataset.

        Args:
            size_dataset (int): The total number of images in the dataset.
            sur (int): The radius of the context window.

        Returns:
            dict: A dictionary where the key is the integer representation of each image
                and the value is a list of integer representation of image within a given radius.
        """
        same_video = {}
        if self.path_ends:
            bottom = 0
            with open(self.path_ends, 'r') as f:
                for line in f:
                    top = int(line[:-1]) - 1
                    same_video.update(
                        {i: [max(bottom, i - sur), min(top, i + sur)] for i in range(bottom, top)})
                    bottom = top
        else:
            for i in range(size_dataset):
                same_video[i] = [i, i]

        return same_video

    def set_finding(self, size_dataset):
        """
        Generate indexes of images that should be found.

        Args:
            size_dataset (int): The total number of images in the dataset.

        Returns:
            list: A list of indexes of images that should be found.
        """
        # images that should be found
        if self.is_sea_database:
            with open(self.path_selection, 'r') as file:
                sea_finding = [int(num) for num in file.readline().split(',')]
            random.shuffle(sea_finding)

        targets = sea_finding[:20] if self.is_sea_database else []
        for i in range(NUMBER_OF_SEARCHED):
            new_int = random.randint(1, size_dataset)
            if new_int not in targets:
                targets.append(new_int)

        return targets

    @staticmethod
    def load_first_screen(class_data, size_dataset, targets):
        """
        Generate the initial set of images indexes using SOM of class labels.

        Args:
            class_data (dict): A dictionary containing the class labels for each image. (used by SOM)
            size_dataset (int): The size of the dataset.
            targets (list): A list of indexes of images that should be found.

        Returns:
            list: A list of indexes of images representing the first window.
        """
        # get first window - SOM of labels
        first_show = [0 for _ in range(IMAGES_ON_LINE * LINES)]
        input_data = np.array(list(class_data.values()))
        som = SOM(m=LINES, n=IMAGES_ON_LINE, dim=len(input_data[0]))

        prediction = som.fit_predict(input_data)

        for i in range(len(first_show)):
            if i in prediction:
                first_show[i] = np.random.choice(np.where(prediction == i)[0])
            else:
                first_show[i] = -1

        for i in range(len(first_show)):
            if first_show[i] == -1 and len((set(first_show) & set(targets)) - {-1}) < size_dataset:
                next_id = random.randint(1, size_dataset - 1)
                while next_id in first_show:
                    next_id = random.randint(1, size_dataset - 1)
                first_show[i] = next_id

        return first_show
