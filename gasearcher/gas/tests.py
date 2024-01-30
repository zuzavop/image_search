import random
from unittest.mock import Mock

import clip
import numpy as np
import torch
from PIL import Image
from django.test import TestCase
from gas.models import size_dataset
from gas.searcher import Searcher
from gas.settings import PATH_DATA


class SearcherTest(TestCase):
    def setUp(self):
        self.clip_data = np.array([[1, 0, 0], [0, 1, 0], [0, 0, 1]])
        self.logger = Mock()
        self.searcher = Searcher(self.clip_data, False, self.logger, 2)

    def result_score_test(self):
        """
        Test the result score calculation function.

        Raises:
            AssertionError: If the test fails.
        """
        features = np.array([1, 0, 0])
        expected_result = [0, 1, 1]
        result = self.searcher.result_score(features.T)

        self.assertListEqual(expected_result, result.tolist())

    def valid_data_test(self):
        """
        Test the validity of the given image and its associated vector.

        Raises:
            AssertionError: If the test fails.
        """
        image_id = random.randint(1, size_dataset)
        image_path = PATH_DATA + "photos//" + str(image_id).zfill(5) + ".jpg"
        vector_path = PATH_DATA + "clip//" + str(image_id).zfill(5) + ".pt"

        # clip
        device = "cuda" if torch.cuda.is_available() else "cpu"
        model, preprocess = clip.load("ViT-B/32", device=device)

        image = preprocess(Image.open(image_path)).unsqueeze(0).to(device)

        with torch.no_grad():
            image_features = model.encode_image(image)
        image_features /= np.linalg.norm(image_features)

        # Check that the computed image features match the expected features
        self.assertEqual(image_features, torch.load(vector_path))
