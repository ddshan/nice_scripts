import os, glob
from urllib.request import urlretrieve
from tqdm import tqdm

dataset_path = f"../hand_video_dataset_v2/"
#genre_folder_path = glob.glob(f"../hand_video_dataset_v2/*_*")
#video_id_folder_path = glob.glob(f"../hand_video_dataset_v2/*_*/*")
video_id_folder_list = glob.glob(f"../hand_video_dataset_v2/*_*/*")
print(len(video_id_folder_list))

for item in tqdm(video_id_folder_list):
    video_id = item.split("/")[-1]

    try:
        url0 = "https://img.youtube.com/vi/" + video_id + "/" + str(0) +".jpg"
        url1 = "https://img.youtube.com/vi/" + video_id + "/" + str(1) +".jpg"
        url2 = "https://img.youtube.com/vi/" + video_id + "/" + str(2) +".jpg"
        url3 = "https://img.youtube.com/vi/" + video_id + "/" + str(3) +".jpg"

        filename0 = item + "/" + video_id + "_" + str(0) +".jpg"
        filename1 = item + "/" + video_id + "_" + str(1) +".jpg"
        filename2 = item + "/" + video_id + "_" + str(2) +".jpg"
        filename3 = item + "/" + video_id + "_" + str(3) +".jpg"

        #print(item, video_id, filename0)

        urlretrieve(url0, filename0)
        urlretrieve(url1, filename1)
        urlretrieve(url2, filename2)
        urlretrieve(url3, filename3)
        
    except:
        print(f"\n{video_id} fail ...\n")