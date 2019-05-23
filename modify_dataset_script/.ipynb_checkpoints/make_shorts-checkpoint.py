import cv2, os, sys
sys.path.append("/x/dandans/try_pyfasterrcnn/faster-rcnn.pytorch/")
from demo_handscore import main_demo

with open("selected_500.txt", "r") as f:
    for video_path in f:
        video_path, duration = video_path.strip().split(" ")
        vid = video_path.split("/")[3].split("_", 2)[2][:-4]
        
        # write all frames into a floder in dev/shm
        output_folder = f"/dev/shm/{vid}" 
        if not os.path.exists(output_folder):
            os.mkdir(output_folder)
        output_path = f"/dev/shm/{vid}/%06d.jpg" 
#         cmd = f"ffmpeg -i {video_path} {output_path}"
#         if (os.system(cmd) == 0):
#             print("success for one video!")
            
        # faster rcnn        
        _, _, num_handfram, hand_num_list = main_demo(output_folder, vid)
        
        # get the list, not choose the range
        short_range_list = []
        index_list = [index for index, item in enumerate(hand_num_list) if item > 0]
        for ind, item in enumerate(index_list[:-1]):
            if index_list[ind+1] - item > 250:
                short_range_list.append( (item, index_list[ind+1]) )
        # create shorts
        for index, short_range in enumerate(short_range_list):
            
        
        
        print(video_path, vid, duration)
        print(hand_num_list)
        print(len(hand_num_list))
        break