import glob
import os
from tqdm import tqdm

video_folder_list = glob.glob("../hand_video_dataset_v2/*_*")
print(video_folder_list)
for video_folder in tqdm(video_folder_list):
    genre = video_folder.split("/")[-1].split("_")[0]
    video_list = glob.glob(f"{video_folder}/*/*.mp4")
    print(f"{genre} len = {len(video_list)}")

    output_folder = f"../hand_video_dataset_v2/ffprobe_json/{genre}_ffprob"
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)

    for ind, video_path in enumerate(video_list):
        video_name = video_path.split("/")[-1][:-4]
        output_path = f"{output_folder}/{video_name}.json"
        cmd = f"ffprobe -v fatal -show_error -show_format -show_streams -print_format json {video_path} > {output_path}"
        os.system(cmd)

        
        
        