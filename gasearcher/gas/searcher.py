import math

import clip
import numpy as np
import torch


class Searcher:
    """
    The Searcher class is responsible for searching through a given set of images using text or image queries.
    It utilizes the CLIP (Contrastive Language-Image Pre-training) model to encode text queries to n-dimensional space.

    Attributes:
        clip_data (list): A list of feature vectors representing the images.
        combination (bool): A boolean flag indicating whether to combine the scores of the current and previous search
            queries. If True, the last search scores are added to the current scores.
            If False, only the current scores are used.
        logger (Logger): A Logger instance for logging search queries and results.
        showing (int): The number of top search results which are display.
        last_search (dict): A dictionary to store the vectors of the last text search for each session.
        device: A string indicating whether to use CPU or GPU for running the CLIP model.
        model: The pre-trained CLIP model.
    """

    def __init__(self, clip_data, combination, logger, showing):
        """
        Args:
            clip_data (list): A list of feature vectors representing the images.
            combination (bool): A boolean flag indicating whether to combine the scores of the current and previous
                search queries.
            logger (Logger): A Logger instance for logging search queries and results.
            showing (int): The number of top search results which are display.
        """
        self.clip_data = clip_data
        self.combination = combination
        self.last_search = {}  # vectors of last text search
        self.logger = logger
        self.showing = showing
        self.last_sent = {}
        self.last_scores = {}
        self.alpha = 0.1
        self.index = 1
        # clip
        self.device = "cuda" if torch.cuda.is_available() else "cpu"
        self.model, preprocess = clip.load("ViT-B/32", device=self.device)

    def result_score(self, features):
        """
        Calculate the similarity distance of the query feature vector to the CLIP data
        (normalize feature vectors of images).

        Args:
            features (numpy.ndarray): A 2D array representing the normalize feature vector of the query.

        Returns:
            numpy.ndarray: A 1D array representing the similarity distance (from 0 to 2) of each image to the query.
        """
        return np.concatenate([1 - (torch.cat(self.clip_data) @ features)], axis=None)

    def text_search(self, query, session, found, activity):
        """
        Text search using CLIP data.

        Args:
            query (str): The text query.
            session (str): The unique session ID of the user. (used for logging)
            found (int): The index of the currently searching image. (used for logging)
            activity (str): The activity from the user. (used for logging)

        Returns:
            list: A list of indices representing the top search results.
        """
        # get normalize features of text query
        with torch.no_grad():
            text_features = self.model.encode_text(clip.tokenize([query]).to(self.device))
        text_features /= np.linalg.norm(text_features)

        # get distance of vectors
        scores = self.result_score(text_features.T)

        new_scores = (scores + self.last_search[session]) if self.combination else scores
        self.last_scores[session] = new_scores[:self.showing]
        new_scores = list(np.argsort(new_scores))

        # save score for next search
        if self.combination:
            self.last_search[session] = scores

        self.logger.log_text_query(query, new_scores, found, session, activity)

        return new_scores[:self.showing]

    def temporal_search(self, query, session, found):
        """
        Temporal search using CLIP data.

        Args:
            query (str): The text query.
            session (str): The unique session ID of the user. (used for logging)
            found (int): The index of the currently searching image. (used for logging)

        Returns:
            list: A list of indices representing the top search results.
        """
        query = query.split(">")
        query1 = query[0]
        query2 = query[1]

        # get normalize features of text query
        with torch.no_grad():
            text_features1 = self.model.encode_text(clip.tokenize([query1]).to(self.device))
            text_features2 = self.model.encode_text(clip.tokenize([query2]).to(self.device))
        text_features1 /= np.linalg.norm(text_features1)
        text_features2 /= np.linalg.norm(text_features2)

        # get distance of vectors
        scores1 = self.result_score(text_features1.T)
        scores2 = self.result_score(text_features2.T)

        scores = [a + (max(scores2[i + 1:i + 4]) if i < len(scores2) - 1 else 2) for i, a in enumerate(scores1)]
        self.last_scores[session] = scores[:self.showing]
        scores = list(np.argsort(scores))

        # save score for next search
        if self.combination:
            self.last_search[session] = scores

        new_return = list(
            [a for i in scores[:self.showing] for a in [i - 2, i - 1, i, i + 1, i + 2, i + 3, i + 4, i + 5]])

        return new_return[:self.showing]

    def image_search(self, image_query, found, session):
        """
        Image search using CLIP data.

        Args:
            image_query (int): The index of the image query.
            found (int): The index of the currently searching image. (used for logging)
            session (str): The unique session ID of the user. (used for logging)

        Returns:
            list: A list of indices representing the top search results.
        """
        # get features of image query
        image_query_index = int(image_query)
        image_query_features = np.transpose(self.clip_data[image_query_index])

        scores = self.result_score(image_query_features)
        self.last_scores[session] = scores[:self.showing]
        scores = list(np.argsort(scores))

        self.logger.log_image_query(image_query, scores, found, session)

        return scores[:self.showing]

    def bayes_update(self, like_image, session):
        """
        Bayes update using selected image.

        Args:
            like_image (int): The index of the selected image.
            session (str): The unique session ID of the user. (used for logging)

        Returns:
            list: A list of indices representing the top results after bayes update.
        """
        # get features of image query
        positive_image = int(like_image)
        dataset = [self.clip_data[i] for i in self.last_sent[session]]
        negative_examples = [self.clip_data[i] for i in self.last_sent[session] if i != positive_image]
        positive_examples = [self.clip_data[positive_image]]

        negative = {str(i): np.concatenate([1 - (torch.cat(negative_examples) @ item.T)], axis=None) for
                    i, item in enumerate(dataset)}
        positive = {str(i): np.concatenate([1 - (torch.cat(positive_examples) @ item.T)], axis=None) for
                    i, item in enumerate(dataset)}

        scores = np.zeros(len(dataset))
        if session in self.last_scores:
            scores = [(1 + d) ** self.index for d in self.last_scores[session]]
        for i in range(len(dataset)):
            div_sum = 0
            for neg in negative[str(i)]:
                div_sum += math.exp(- neg / self.alpha)

            for pos in positive[str(i)]:
                PF = math.exp(- pos / self.alpha)
                scores[i] *= (PF / (div_sum + PF))

        scores = [self.last_sent[session][i] for i in list(np.argsort(scores))[::-1]]

        return scores[:self.showing]

    def reset_last(self, session):
        """
        Reset scores of last search for user of given session.

        Args:
            session (str): The unique session ID of the user.
        """
        self.last_search[session] = np.zeros(len(self.clip_data))
