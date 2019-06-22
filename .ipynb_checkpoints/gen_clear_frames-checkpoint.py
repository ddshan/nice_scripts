'''
@Author: Dandan Shan
@Date: 2019-06-21 22:08:32
@LastEditTime: 2019-06-21 22:17:33
@Descripation: gen clear frames
'''

import glob, os, sys
from tqdm import tqdm

short_list1 = glob.glob("/x/dandans/short_videos/*/*.mp4")
short_list2 = glob.glob("/x/dandans/short_videos/*/*/*.mp4")
short_list = short_list1 + short_list2
#print(short_list)
print(len(short_list))

save_folder = "./frame_cache_HD"

for a_path in short_list:
    video_name = a_path.split("/")[-1][:-4]
    output_path = f"/x/dandans/nice_script/frame_cache_HD/{video_name}/{video_name}_%06d.jpg"
    output_path_folder = f"/x/dandans/nice_script/frame_cache_HD/{video_name}"
    print(a_path, video_name, output_path) 
    
    if not os.path.exists(output_path_folder):
        os.makedirs(output_path_folder)
    
    # ffmpeg -i inputfile.avi -r 1 -f image2 image-%05d.jpeg 
    cmd = f"./../try_pyfasterrcnn/ffmpeg-git-20190514-amd64-static/ffmpeg -i {a_path} -q:v 2 {output_path}"
    print(cmd)
    if (os.system(cmd) == 0):
        print(f"@@@@@@@@@@@@@@@@@ success extraction for {vid}!")
    
    break