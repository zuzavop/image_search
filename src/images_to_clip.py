import clip
import numpy as np
import torch
from PIL import Image

device = "cuda" if torch.cuda.is_available() else "cpu"
model, preprocess = clip.load("ViT-B/32", device=device)


def get_vector_from_photo(photo_path, photo_name, result_path):
    """
    Extracts a feature vector from an input photo and saves it to a .pt file.

    Args:
        photo_path (str): The file path of the input photo.
        photo_name (str): The name of the input photo.
        result_path (str): The directory path where the output .pt file will be saved.
    """
    image = preprocess(Image.open(photo_path)).unsqueeze(0).to(device)

    with torch.no_grad():
        image_feat = model.encode_image(image)
        image_feat = image_feat / np.linalg.norm(image_feat)
        torch.save(image_feat, result_path + f"//{photo_name}.pt")

    print(photo_name)
