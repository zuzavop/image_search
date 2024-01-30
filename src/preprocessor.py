import os

import clip
import torch

from images_to_clip import get_vector_from_photo
from parse_video import parse_video
from top_classes import classify_images


class Preprocessor:
    def __init__(self, videos_path, result_path):
        """
        Initializes a Preprocessor.

        Args:
            videos_path (str): The path to the directory containing the videos to be parsed.
            result_path (str): The path to the directory where the results will be saved.
        """
        self.videos_path = videos_path
        self.result_path = result_path
        self.photos_path = result_path + "photos//"
        if not os.path.exists(self.photos_path):
            os.makedirs(self.photos_path)
        self.vectors_path = result_path + "clip//"
        if not os.path.exists(self.vectors_path):
            os.makedirs(self.vectors_path)

    def parse_videos(self, enable_logging, log_path="videos.txt"):
        """
        Recursively parses a directory of videos and extracts frames from them.

        Args:
            enable_logging (bool): A flag indicating whether logging is enabled or not.
            log_path (str): The path to the log file where information about end of each video will be written.
        """
        for filename in os.listdir(self.videos_path):
            if os.path.isdir(filename):
                self.parse_videos(enable_logging, log_path)
            else:
                parse_video(self.videos_path + "//" + filename, self.photos_path, enable_logging, log_path)

    def images_to_vectors(self):
        """
        Converts images (.jpg) to vectors using CLIP.
        """
        for photo in os.listdir(self.photos_path):
            get_vector_from_photo(self.photos_path + photo, photo[:-4], self.vectors_path)

    def nounlist_to_vectors(self, nounlist_path, output_name):
        """
        Converts a list of nouns into their vector representations using the CLIP.

        Args:
            nounlist_path (str): The path to the file containing a dictionary with classes.
            output_name (str): The name of the file to write the resulting vector representations to.
        """
        device = "cuda" if torch.cuda.is_available() else "cpu"
        model, preprocess = clip.load("ViT-B/32", device=device)

        with open(nounlist_path) as f:
            idx2label = [line.strip() for line in f]

        text_inputs = torch.cat([clip.tokenize(f"a photo of {c}") for c in idx2label]).to(device)

        with torch.no_grad():
            text_features = model.encode_text(text_inputs)
        text_features /= text_features.norm(dim=-1, keepdim=True)

        torch.save(text_features, self.result_path + output_name)

    def classify_images(self, nounlist_path, result_file, new_nounlist_name):
        """
        Classifies images using a CLIP model and saves the results to a file.

        Args:
            nounlist_path (str): The path to the noun list file used for classification.
            result_file (str): The path to the file where the classification results will be saved.
            new_nounlist_name (str): The name of file to which will be writen nounlist with frequency of each class.
        """
        self.nounlist_to_vectors(nounlist_path, self.result_path + "nounlist.pt")
        classify_images(self.vectors_path, self.result_path + "nounlist.pt", result_file)
        self.get_class_pr(nounlist_path, result_file, new_nounlist_name)

    @staticmethod
    def get_class_pr(nounlist_path, classification_path, result_filename):
        """
        Computes the probability distribution of image classifications in a dataset.

        Args:
            nounlist_path (str): The path to the file containing a dictionary with classes.
            classification_path (str): The path to the file containing the classification of each image in the dataset.
            result_filename (str): The name of the file to write the classification probabilities with classes names to.
        """
        with open(nounlist_path) as f:
            words = [line.strip() for line in f]

        most_common = {i: 0 for i in range(len(words))}
        photos_count = 0

        with open(classification_path) as f:
            for line in f:
                line = (line.split(';')[1])[1:-2].split(',')
                for i in line:
                    most_common[int(i)] += 1
                photos_count += 1

        with open(result_filename, 'a') as f:
            for k, v in most_common.items():
                f.write(f"{words[int(k)]} : {v / photos_count * 100:.3f}\n")

    @staticmethod
    def rename_images(images_path, name_format='{:05d}'):
        """
        Renames images in a directory to a specified format.

        Args:
            images_path (str): The path to the directory containing the images to be renamed.
            name_format (str): The format string to use for the new image names. Default is '{:05d}'.
        """
        i = 1
        for file in os.listdir(images_path):
            os.rename(images_path + file, images_path + name_format.format(i) + ".jpg")
            i += 1

    def preprocess_dataset(self, nounlist_path):
        """
        Preprocesses a dataset by parsing the videos, extracting frames, converting them to vectors,
        classifying the vectors, and saving the results to a file.

        Args:
            nounlist_path (str): The path to the noun list file used for classification.
        """
        self.parse_videos(True, self.result_path + "videos_end.txt")
        self.rename_images(self.photos_path)
        self.images_to_vectors()
        self.classify_images(nounlist_path, self.result_path + "result.csv", self.result_path + "nounlist.txt")


preprocessor = Preprocessor(".//data//videos", ".//data//")
preprocessor.preprocess_dataset("..//nounlists//nounlist.txt")
