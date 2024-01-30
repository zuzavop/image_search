import os

import clip
import torch

# load the model
device = "cuda" if torch.cuda.is_available() else "cpu"
model, preprocess = clip.load('ViT-B/32', device)


def classify_images(vectors_path, nounlist_path, result_file, top_k=10):
    """
    Classifies images by comparing their features obtained from CLIP model to the features of each class
    (also obtained from the same CLIP model).

    Args:
        vectors_path (str): The path to the directory containing the image features obtained from the CLIP model.
        nounlist_path (str): The path to the nounlist dataset features obtained from the CLIP model.
        result_file (str): The path to the file where the results will be stored.
        top_k (int): The number of top classes to return for each image.
    """
    # load nounlist (text dataset) features
    text_features = torch.load(nounlist_path)

    # write header
    with open(result_file, 'a') as f:
        f.write("id;top\n")

    for fn in os.listdir(vectors_path):
        filename = vectors_path + "/" + fn
        # load image features get from clip
        image_features = torch.load(filename)

        # get top k classes for image
        similarity = (100.0 * image_features @ text_features.T)
        values, indices = similarity[0].topk(top_k)

        with open(result_file, 'a') as f:
            f.write(fn[:-3] + ';' + str(list(indices.numpy())) + '\n')
