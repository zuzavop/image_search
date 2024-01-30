import csv
import os
import sys

import clip
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import seaborn as sns
import torch
from matplotlib import ticker


class Evaluator:
    """
    A class for evaluating models and visualizing results.

    Attributes:
        device (str): The device on which the model is loaded.
        model: The loaded model.
        preprocess: The preprocessing function of the loaded model.
        clip_data (list): A list of data extracted from images.
        same_video (dict): A dictionary mapping video names to their surrounding.
        last_search (dict): A dictionary mapping sessions to their last searched query.
        multi_search (dict): A dictionary mapping sessions to their last searched queries for multi model.
        min_search (dict): A dictionary mapping sessions to their last search query for min model.
    """

    def __init__(self, result_path, clip_path, showing=60, has_sur=True, surrounding=7,
                 sur_path="videos_end.txt"):
        """
        Initializes the Evaluator object.

        Args:
            result_path (str): Path to the directory where the results will be stored.
            clip_path (str): Path to the directory where the clip data will be loaded from.
            showing (int): The number of images to be shown in the result.
            has_sur (bool): Whether to use surrounding of images.
            surrounding (int): How much surrounding images to use.
            sur_path (str): Path to the file which define ends of each video.
        """
        self.device = "cuda" if torch.cuda.is_available() else "cpu"
        self.model, self.preprocess = clip.load("ViT-B/32", device=self.device)
        self.result_path = result_path
        self.showing = showing
        self.sur = surrounding

        self.clip_data = []
        self.same_video = {}
        self.last_search = {}
        self.multi_search = {}
        self.min_search = {}

        for fn in sorted(os.listdir(clip_path)):
            self.clip_data.append(torch.load(clip_path + f"/{fn}"))

        if has_sur:
            bottom = 0
            with open(sur_path, 'r') as f:
                for line in f:
                    top = int(line.strip()) - 1
                    self.same_video.update(
                        {i: [max(bottom, i - self.sur), min(top, i + self.sur)] for i in range(bottom, top)})
                    bottom = top
        else:
            self.same_video = {i: [i, i] for i in range(len(self.clip_data))}

        self.logger = Logger(showing, self.same_video, self.result_path)

    def evaluate_data(self, log_path, reform_count=2, with_som=False, is_sea=False, with_limited=False):
        """
        Evaluates the data from given log for each model define in project.

        Args:
            log_path (str): Path to the log file.
            reform_count (int): How many times the text query can be reformulated.
            with_som (bool): Whether the Self-Organizing Map is used for generating first screen.
            is_sea (bool): Whether the sea dataset is used.
            with_limited (bool): Defines whether models should be evaluated for a limited dataset.
        """
        query_count = 0
        previous_id = -1
        previous_session_id = ""
        same_count = 0

        with open(log_path) as csv_file:
            csv_reader = csv.reader(csv_file, delimiter=';')
            next(csv_reader)  # skip header

            for row in csv_reader:
                current_id = int(row[1])
                current_session = row[2]

                # change of user or searched image
                if previous_id != current_id or previous_session_id != current_session:
                    query_count += 1
                    same_count = 1
                    self.last_search[current_session] = np.zeros(len(self.clip_data))
                    self.min_search[current_session] = np.full(len(self.clip_data), 2)
                    self.multi_search[current_session] = np.ones(len(self.clip_data))
                else:
                    same_count += 1

                if same_count <= reform_count:
                    self.get_data_from_text_search(row[0], current_session, current_id, same_count == 2,
                                                   with_som, is_sea, with_limited)

                previous_id = current_id
                previous_session_id = current_session

        print("Total search: ", query_count)

    def get_data_from_text_search(self, query, session, found, is_second, with_som, is_sea, with_limited):
        """
        Gets data for a current text search and log search for all models.

        Args:
            query (str): The text query used for search.
            session (str): The id of current session.
            found (int): The id of the image that was currently looking for.
            is_second (bool): Whether this is the second text query.
            with_som (bool): Whether the Self-Organizing Map is used for generating first screen.
            is_sea (bool): Whether the sea dataset is used.
            with_limited (bool): Defines whether models should be evaluated for a limited dataset.
        """
        # get features of text query
        with torch.no_grad():
            text_features = self.model.encode_text(clip.tokenize(['"' + query + '"']).to(self.device))
        text_features /= np.linalg.norm(text_features)

        # get distance of vectors
        scores = np.concatenate([1 - (torch.cat(self.clip_data) @ text_features.T)], axis=None)

        self.log_text_search_for_all_models(scores, query, session, found, is_second, with_som, is_sea)

        if with_limited:
            self.log_text_search_for_all_models(scores, query, session, found, is_second, with_som, is_sea, 0.25)
            self.log_text_search_for_all_models(scores, query, session, found, is_second, with_som, is_sea, 0.5)
            self.log_text_search_for_all_models(scores, query, session, found, is_second, with_som, is_sea, 0.75)

        self.last_search[session] = scores
        self.multi_search[session] = scores
        self.min_search[session] = scores

    def log_text_search_for_all_models(self, scores, query, session, found, is_second, with_som, is_sea, limit=1.0):
        """
        Logs the text search for all models.

        Args:
            scores (numpy.ndarray): The scores of the text search.
            query (str): The text query used for search.
            session (str): The id of current session.
            found (int): The id of the image that was currently looking for.
            is_second (bool): Whether this is the second text query.
            with_som (bool): Whether the Self-Organizing Map is used for generating first screen.
            is_sea (bool): Whether the sea dataset is used.
            limit (float): The percentage limit for dataset after first query.
        """
        indexes = np.arange(len(self.clip_data))
        min_search = self.min_search[session]
        last_search = self.last_search[session]
        multi_search = self.multi_search[session]

        if is_second:
            indexes = np.argsort(self.last_search[session])[:int(len(self.clip_data) * limit)]
            scores = scores[indexes]
            min_search = min_search[indexes]
            last_search = last_search[indexes]
            multi_search = multi_search[indexes]

        # implementation of fusion of each models
        self.logger.log_down_text_search(self.get_log_name("basic", with_som, is_sea, limit), list(np.argsort(scores)),
                                         indexes, query, session, found)
        self.logger.log_down_text_search(self.get_log_name("min", with_som, is_sea, limit),
                                         list(np.argsort(np.min(np.array([scores, min_search]), axis=0))), indexes,
                                         query, session, found)
        self.logger.log_down_text_search(self.get_log_name("max", with_som, is_sea, limit),
                                         list(np.argsort(np.max(np.array([scores, last_search]), axis=0))), indexes,
                                         query, session, found)
        self.logger.log_down_text_search(self.get_log_name("sum", with_som, is_sea, limit),
                                         list(np.argsort(scores + last_search)), indexes, query, session, found)
        self.logger.log_down_text_search(self.get_log_name("multi", with_som, is_sea, limit),
                                         list(np.argsort(scores * multi_search)), indexes, query, session, found)
        self.logger.log_down_text_search(self.get_log_name("avg", with_som, is_sea, limit),
                                         list(np.argsort((2 * scores) + last_search)), indexes, query, session, found)

    @staticmethod
    def get_log_name(name, is_som, is_sea, limit=1.0):
        """
        Gets the name for the log.

        Args:
            name (str): The name of the model.
            is_som (bool): Whether the Self-Organizing Map is used for generating first screen.
            limit (float): The percentage limit for dataset after first query.
            is_sea (bool): Whether the sea dataset is used.

        Returns:
            str: The name for the log.
        """
        if is_sea:
            name = "sea_" + name
        if is_som:
            name += "_som"
        if limit < 1.0:
            name += "_limit_" + str(25 if limit == 0.25 else (50 if limit == 0.5 else 75))
        return name + ".csv"

    def get_data_from_log(self, log_path, filter_undefined, filter_findable, use_surrounding):
        """
        Method to extract data from a log file.

        Args:
            log_path (str): Path to the log file.
            filter_undefined (bool): Define if undefined values should be filtered out.
            filter_findable (bool): Defines whether to filter out data that can be found by the first query.
            use_surrounding (bool): Defines whether to use the rank of frame and its surroundings.

        Returns:
            A list containing the ranks for second query, ranks for first query, and difference values
            extracted from the log file.
        """
        position_of_rank = 5 if use_surrounding else 3
        ranks1 = []
        ranks2 = []
        with open(log_path) as csv_file:
            csv_reader = csv.reader(csv_file, delimiter=';')
            line = 0

            previous_row = {}

            for row in csv_reader:
                if line > 0 and row[1] == previous_row[1] and row[2] == previous_row[2]:
                    if ((filter_undefined and int(row[position_of_rank]) > 0) or not filter_undefined) and (
                            (filter_findable and int(
                                int(previous_row[position_of_rank]) > self.showing)) or not filter_findable):
                        ranks1.append(int(previous_row[position_of_rank]) if int(previous_row[position_of_rank]) > 0 else len(self.clip_data))
                        ranks2.append(
                            int(row[position_of_rank]) if int(row[position_of_rank]) > 0 else len(self.clip_data))

                previous_row = row
                line += 1

        return [ranks2, ranks1]

    def get_data_for_graph(self, input_path, first_col_name, with_limited, filter_undefined, filter_findable,
                           use_surrounding):
        """
        Extracts data from multiple log files to be used for generating a plot.

        Args:
            input_path (str): Path to the directory containing the log files.
            first_col_name (str): Name of the first column in the generated plot.
            with_limited (bool): Define if models that are limited should be used for graph
            filter_undefined (bool): Define if undefined values should be filtered out.
            filter_findable (bool): Defines whether to filter out data that can be found by the first query.
            use_surrounding (bool): Defines whether to use the rank of frame and its surroundings.

        Returns:
            A tuple containing the data and column names to be used in generating the plot.
        """
        data = []
        columns = [first_col_name]

        x = 0
        for fn in sorted(os.listdir(input_path)):
            if "limit" in fn and not with_limited:
                continue
            if x == 0:
                data = [self.get_data_from_log(input_path + fn, filter_undefined, filter_findable, use_surrounding)[1]]
            data = np.append(data, [
                self.get_data_from_log(input_path + fn, filter_undefined, filter_findable, use_surrounding)[0]], axis=0)
            columns.append(fn[:-4])
            x += 1

        return [data, columns]

    def get_violin_plot(self, input_path, output_file, first_col_name='1_not_found', use_log_scale=True,
                        with_limited=False, filter_undefined=False, filter_findable=True, use_surrounding=False):
        """
        Generates a violin plot of the data extracted from the log files.

        Args:
            input_path (str): Path to the directory containing the log files.
            output_file (str): Path to the output file to save the plot.
            first_col_name (str): Name of the first column in the generated plot.
            use_log_scale (bool): If plot has log scale.
            with_limited (bool): Define if models that are limited should be used for graph
            filter_undefined (bool): Define if undefined values should be filtered out from used data.
            filter_findable (bool): Defines whether to filter out data that can be found by the first query.
            use_surrounding (bool): Defines whether to use the rank of frame and its surroundings.
        """
        data, columns_name = self.get_data_for_graph(input_path, first_col_name, with_limited, filter_undefined,
                                                     filter_findable, use_surrounding)

        if use_log_scale:
            data = [[np.log10(d) for d in row] for row in data]
        data = pd.DataFrame(np.array(data).T, columns=columns_name)

        fig, ax = plt.subplots(figsize=(16, 5))
        sns.set()
        sns.violinplot(data=data, bw=.02, ax=ax)

        if use_log_scale:
            ax.yaxis.set_major_formatter(ticker.StrMethodFormatter("$10^{{{x:.0f}}}$"))
            ymin, ymax = ax.get_ylim()
            tick_range = np.arange(np.floor(ymin), ymax)
            ax.yaxis.set_ticks(tick_range)
            ax.yaxis.set_ticks([np.log10(x) for p in tick_range for x in np.linspace(10 ** p, 10 ** (p + 1), 10)],
                               minor=True)
            plt.tight_layout()

        plt.savefig(output_file)

    def get_points_plot(self, input_path, output_file, first_col_name='1_not_found', use_log_scale=True,
                        with_limited=False, filter_undefined=False, filter_findable=True, use_surrounding=False):
        """
        Generates a points plot of the data extracted from the log files.

        Args:
            input_path (str): Path to the directory containing the log files.
            output_file (str): Path to the output file to save the plot.
            first_col_name (str): Name of the first column in the generated plot.
            use_log_scale (bool): If plot has log scale.
            with_limited (bool): Define if models that are limited should be used for graph
            filter_undefined (bool): Define if undefined values should be filtered out from used data.
            filter_findable (bool): Defines whether to filter out data that can be found by the first query.
            use_surrounding (bool): Defines whether to use the rank of frame and its surroundings.
        """
        data, columns_name = self.get_data_for_graph(input_path, first_col_name, with_limited, filter_undefined,
                                                     filter_findable, use_surrounding)
        data = pd.DataFrame(np.array(data).T, columns=columns_name)

        sns.set()
        sns.stripplot(data=data)
        if use_log_scale:
            plt.yscale('log')
        plt.savefig(output_file)

    def get_boxen_plot(self, input_path, output_file, first_col_name='1_not_found', use_log_scale=True,
                        with_limited=False, filter_undefined=False, filter_findable=True, use_surrounding=False):
        """
        Generates a boxen plot of the data extracted from the log files.

        Args:
            input_path (str): Path to the directory containing the log files.
            output_file (str): Path to the output file to save the plot.
            first_col_name (str): Name of the first column in the generated plot.
            use_log_scale (bool): If plot has log scale.
            with_limited (bool): Define if models that are limited should be used for graph
            filter_undefined (bool): Define if undefined values should be filtered out from used data.
            filter_findable (bool): Defines whether to filter out data that can be found by the first query.
            use_surrounding (bool): Defines whether to use the rank of frame and its surroundings.
        """
        data, columns_name = self.get_data_for_graph(input_path, first_col_name, with_limited, filter_undefined,
                                                     filter_findable, use_surrounding)
        data = pd.DataFrame(np.array(data).T, columns=columns_name)

        sns.set()
        sns.boxenplot(data=data)
        if use_log_scale:
            plt.yscale('log')
        plt.savefig(output_file)

    def get_combine_plot(self, input_path, output_file, first_col_name='1_not_found', use_log_scale=True,
                        with_limited=False, filter_undefined=False, filter_findable=True, use_surrounding=False):
        """
        Generates a combine plot (violin plot combine with swarm plot) of the data extracted from the log files.

        Args:
            input_path (str): Path to the directory containing the log files.
            output_file (str): Path to the output file to save the plot.
            first_col_name (str): Name of the first column in the generated plot.
            use_log_scale (bool): If plot has log scale.
            with_limited (bool): Define if models that are limited should be used for graph
            filter_undefined (bool): Define if undefined values should be filtered out from used data.
            filter_findable (bool): Defines whether to filter out data that can be found by the first query.
            use_surrounding (bool): Defines whether to use the rank of frame and its surroundings.
        """
        data, columns_name = self.get_data_for_graph(input_path, first_col_name, with_limited, filter_undefined,
                                                     filter_findable, use_surrounding)
        data = pd.DataFrame(np.array(data).T, columns=columns_name)

        sns.set()
        sns.catplot(data=data, kind="violin", color=".9", inner=None, cut=0, bw=.02)
        sns.swarmplot(data=data, size=1.5)
        if use_log_scale:
            plt.yscale('log')
        plt.savefig(output_file)


class Logger:
    def __init__(self, showing, same_video, result_path):
        """
        Initializes a Logger object.

        Args:
            showing (int): The number of images to be shown in the result.
            same_video (dict): A dictionary containing the indices surrounding image (surrounding in same video).
            result_path (str): The directory path where the log files will be saved.
        """
        self.showing = showing
        self.same_video = same_video
        self.result_path = result_path + "\\model_results\\"
        if not os.path.exists(self.result_path):
            os.makedirs(self.result_path)

    def log_down_text_search(self, log_filename, new_result, indexes, query, session, found):
        """
        Writes the result of a query to a log file.

        Args:
            log_filename (str): The name of the log file.
            new_result (list): A list of indices (mapped to indexes list) sorted by similarity to the current query.
            indexes (list): A list of indices of all images in the dataset that are currently used.
            query (str): The text of the query.
            session (str): The id of the user session.
            found (int): The index of the image that was currently looking for.
        """
        with open(self.result_path + log_filename, "a") as log:
            # if searching image is present in context (surrounding of image) of any image in shown result same is equal 1
            first = self.get_rank(new_result, np.where(indexes == found)[0][0]) if found in indexes else sys.maxsize
            for i in list(
                    set(indexes).intersection(set(np.arange(self.same_video[found][0], self.same_video[found][1])))):
                first = min(first, self.get_rank(new_result, np.where(indexes == i)[0][0]))

            log.write(f'"{query}";{found};{session};' + str(self.get_rank(new_result, np.where(indexes == found)[0][
                0]) if found in indexes else -1) + f';{first if first < sys.maxsize else -1}\n')

    @staticmethod
    def get_rank(result, index):
        """
        Get rank (from 1) of image.

        Args:
            result (list): A list of indices of images sorted by similarity to the current query
            index (int): The index of the image

        Returns:
            int: The rank of given image
        """
        return result.index(index) + 1


evaluator = Evaluator(".//", "..//gasearcher//static//data//clip", 60, True, 2,
                      "..//gasearcher//static//data//videos_end.txt")
evaluator.evaluate_data("..//gasearcher//static//data//log.csv")
evaluator.get_violin_plot(".//model_results//", "plot.png")
