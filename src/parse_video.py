import glob
import os


def get_latest_index(output_path):
    """
    Given a path to a directory containing image files, returns the index of the latest image file.

    Args:
        output_path (str): Path to the directory containing the image files.

    Returns:
        int: The index of the latest image file.
    """
    list_of_files = glob.glob(output_path + "*")
    if not list_of_files:
        return 1
    latest_file = max(list_of_files, key=os.path.getctime).split('\\')[-1]
    return int(latest_file[:-4]) + 1


def get_comm(video_path, output_path, start_index, is_wide=True):
    """
    Returns the FFmpeg command to extract frames from a video.

    Args:
        video_path (str): Path to the input video file.
        output_path (str): Path to the directory where the output image files will be saved.
        start_index (int): Index of the first image file.
        is_wide (bool): Defines whether the video is landscape.

    Returns:
        str: The FFmpeg command to extract frames from the input video.
    """
    if is_wide:
        comm = 'ffmpeg -i {0} -vf "fps=0.5,scale=224:-1,crop=in_w:224:0:in_h/2-112" -start_number {1} {2}'.format(video_path, start_index, output_path + "%9d.jpg")
        print(video_path)
    else:
        comm = 'ffmpeg -i {0} -vf "fps=0.5,scale=-1:224,crop=224:in_h:in_w/2-112:0" -start_number {1} {2}'.format(video_path, start_index, output_path + "%9d.jpg")
    return comm


def parse_video(video_path, output_path, logging_enable, log_path=""):
    """
    Extracts frames from a video and saves them as image files.

    Args:
        video_path (str): Path to the input video file.
        output_path (str): Path to the directory where the output image files will be saved.
        logging_enable (bool): Indicates whether to enable logging.
        log_path (str): Path to the log file (optional), where index of video end will be print.
    """
    if video_path.endswith(".mp4") or video_path.endswith(".MP4"):
        start_index = get_latest_index(output_path)
        if logging_enable:
            with open(log_path, "a") as log:
                log.write(str(start_index) + "\n")
        if os.system(get_comm(video_path, output_path, start_index)) == 1:
            os.system(get_comm(video_path, output_path, start_index, False))
