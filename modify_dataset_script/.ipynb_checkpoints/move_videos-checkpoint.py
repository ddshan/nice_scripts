# deal with videos in ffprobe_json

import glob, json, os
from tqdm import tqdm
import shutil
from concurrent.futures import ThreadPoolExecutor

def copy_video(src, des):
    shutil.copy2(src, des)
    print(des)


genre_folder_list = glob.glob("./ffprobe_json/*")
genre_list = [ item.split("/")[2] for item in genre_folder_list]
print(genre_list)
print(genre_folder_list)

src_list = []
des_list = []
for genre in genre_list:
    print(genre + "*" *30)
    genre_json_list = glob.glob(f'./ffprobe_json/{genre}/*.json')
    print(f'num of json files = {len(genre_json_list)}')
    for item in genre_json_list:
        a_json_info = json.load(open(item, "r"))
        #
        filename = a_json_info["format"]["filename"]
        duration = int (float( a_json_info["streams"][0]["duration"] ) / 60)
        
        if duration < 30: # move to a new place
            video_name = filename.split("/")[2]
            if video_name.split("_")[0] != genre:
                continue
            vid = video_name.split("_", 2)[2][:-4]
            origin_video_path = f'../picked_video_mp4_folder/{filename[2:]}'
            new_folder_path = f'../hand_video_dataset_v2/{genre}_videos/{vid}'
            if not os.path.exists(new_folder_path):
                os.makedirs(new_folder_path)
            new_video_path = os.path.join(new_folder_path, video_name)
            #print(vid, video_name, origin_video_path, new_video_path)
            src_list.append(origin_video_path)
            des_list.append(new_video_path)
            #shutil.copy2(origin_video_path, new_video_path)
    
print(f"{genre} len of src and des = {len(src_list)} {len(des_list)}")

pool = ThreadPoolExecutor(48)
pool.map(copy_video, src_list, des_list)