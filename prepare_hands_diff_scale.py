import cv2, os, json
import numpy as np
# get center, scale, coordinates
import handutils
from PIL import Image

def get_scaled_bbox(image, annot, scale_factor, res=(256,256)):
    scale = handutils.get_annot_scale(annots=annot, scale_factor=scale_factor )
    center = handutils.get_annot_center(annots=annot)
    affine = handutils.get_affine_trans_no_rot(center, scale, res)
    image = handutils.transform_img(image, affine, res)
    return image

# read res from faster-rcnn
json_file = "./test_results_json/frame_HD_1000.json"
image_folder = "../Dataset/frame_HD_1000"
output_folder = "../Dataset/frame_HD_scaled_hand"
if not os.path.exists(output_folder):
    os.makedirs(output_folder)

with open(json_file, "r") as f:
    bbox_dict = json.load(f)
scale_list = [1.0, 1.3, 1.6, 1.9, 2.2, 2.5]
for index, (key, value) in enumerate(bbox_dict.items()):
    image_path = os.path.join(image_folder, key)
    image = Image.open(image_path)
    for i in range(len(value)):
        bbox = value[i]
        bbox = np.array([[bbox[0], bbox[1]],[bbox[2], bbox[3]]])
        for scale in scale_list:
            scaled_image = get_scaled_bbox(image, bbox, scale)
            scaled_image.save(f"{output_folder}/img{index}_idx{i}_scale{scale}.jpg")
        



    if index == 100: break

    
    