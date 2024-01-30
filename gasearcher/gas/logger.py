import numpy as np

from gas.settings import SHOWING, PATH_LOG, PATH_LOG_SIMILARITY


class Logger:
    """
    Log text and image queries.

    Attributes:
        path_log (str): The path of the log file for queries.
        same_video (dict): A dictionary containing the limit indices bounding images context (surrounding in same video).
        targets (list) : The indexes of images which are searched for.
    """

    def __init__(self, path_data, same_video, targets, is_sea_database):
        """
        Args:
            path_data (str): The path to data.
            same_video (dict): A dictionary containing the limit indices bounding images context (surrounding in same video).
            targets (list): The indexes of images which are searched for.
        """
        self.path_log = path_data + ("sea_log.csv" if is_sea_database else PATH_LOG)
        self.path_log_similarity = path_data + ("sea_log_similarity.csv" if is_sea_database else PATH_LOG_SIMILARITY)
        self.same_video = same_video  # indexes of images in same video (high probability of same looking photos)
        self.targets = targets

    def log_text_query(self, query, new_result, target, session, activity):
        """
        Logs a text query.

        Args:
            query (str): The query text.
            new_result (list): A list of indices of images sorted (in order) by similarity to the current text query.
            target (int): The order of the currently searching image in targets.
            session (str): The unique session ID of the user.
            activity (str): The activity from the user.
        """
        # write down log
        with open(self.path_log, "a") as log:
            log.write(f'{query};{str(self.targets[target])};{session};' + str(
                self.get_rank(new_result, self.targets[target])) + f';"{activity}"\n')

    def log_image_query(self, query_id, new_result, target, session):
        """
        Logs an image query.

        Args:
            query_id (int): The query image ID.
            new_result (list): A list of indices of images sorted (in order) by similarity to the current image query.
            target (int): The order of the currently searching image in targets.
            session (str): The unique session ID of the user.
        """
        # write down log
        with open(self.path_log_similarity, "a") as log:
            log.write(f'{str(query_id)};{str(self.targets[target])};{session};' + str(
                self.get_rank(new_result, self.targets[target])) + ';""\n')

    @staticmethod
    def get_rank(result, index):
        """
        Get rank (from 1) of image.

        Args:
            result (list): A list of indices of images sorted (in order) by similarity to the current query
            index (int): The index of the image

        Returns:
            int: The rank of given image
        """
        return result.index(index) + 1
