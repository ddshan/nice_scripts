import cv2, os, sys
from demo_handscore import main_demo

with open("../../modify_dataset_script/selected_100.txt", "r") as f:
    for video_path in f:
        video_path, duration = video_path.strip().split(" ")  #../picked_video_mp4_folder/drink_videos/drink_887_bo2XrSymaFA.mp4 5
        
        vid = video_path.split("/")[3].split("_", 2)[2][:-4]
        video_path = f"../{video_path}"
        
        # write all frames into a floder in dev/shm
        output_folder = f"/dev/shm/{vid}" 
        if not os.path.exists(output_folder):
            os.mkdir(output_folder)
        output_path = f"/dev/shm/{vid}/%06d.jpg" 
#         cmd = f"./../ffmpeg-git-20190514-amd64-static/ffmpeg -i {video_path} {output_path}"
#         if (os.system(cmd) == 0):
#             print("success for one video!")
            
        # faster rcnn
        _, _, num_handfram, hand_num_list = main_demo(output_folder, vid)
        
        # get the list, not choose the range
        # interval between 2 zero if bigger than 252, take the range
#         nonzero_index_list = [ index for index, item in enumerate(hand_num_list) if item != 0 ]
        hand_range_list = []
        ind1 = 0
        
        
        while ind1 < len(hand_num_list) - 1:   # 0 - (len-2)
            if hand_num_list[ind1] == 0:
                ind1 += 1
                continue
            #print(f"ind1 = {ind1}")
            ind2 = ind1 + 1
            while ind2 < len(hand_num_list):  # 0 - (len-2) : 1 - (len-1)
                #print(f"    ind2 = {ind2}")
                if hand_num_list[ind2] != 0:
                    ind2 += 1
                    continue
                else:
                    inter  = ind2 - ind1
                    ind2 = ind2 -1  # non-zero position
                    if 130 < inter and inter < 300:
                    #if inter > 2:
                        hand_range_list.append( (ind1, ind2) )
                        ind1 = ind2 + 1
                        break
                    else:
                        ind1 = ind2 + 1
                        break
            #print(ind2, len(hand_num_list)-1)
            if ind2 == len(hand_num_list):
                #print(f"the end, ind2 = {ind2}")
                inter  = ind2 - ind1
                if 130 < inter and inter < 300:
                #if inter > 2:
                    hand_range_list.append( (ind1, ind2-1) )
            ind1 = ind2 + 1
                
        print(f"hand_range_list len = {len(hand_range_list)}\n", hand_range_list)
        
        # ffmpeg the range into short videos
        # ffmpeg -framerate 24 -i Project%03d.png Project.mp4
        short_video_folder = f"/x/dandans/short_videos/{vid}"
        if not os.path.exists(short_video_folder):
            os.makedirs(short_video_folder)
        for ind, (start, end) in enumerate(hand_range_list):
            cmd = f"./../ffmpeg-git-20190514-amd64-static/ffmpeg -start_number {start+1:06d} -i {output_folder}/%06d.jpg -vframes {end-start} {short_video_folder}/{vid}_short_{ind}.mp4"
            if (os.system(cmd) == 0):
                print(f"success : {cmd}")
            
        
        print(video_path, vid, duration)
        #print(hand_num_list)
        print(len(hand_num_list))
        break
