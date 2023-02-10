from depth_model.infer import InferenceHelper
from PIL import Image, ImageOps
import numpy as np
import requests
import cv2
def bluring_img(img_url,label,segmentation, blur_strength = 1, split = 100, size = 45):
    image = Image.open(requests.get(img_url, stream=True).raw)
    image = ImageOps.exif_transpose(image) # 이미지 업로드시 회전되는 문제 해결
    image = Image.fromarray(np.array(image)[:,:,0:3])
    ratio = 640 / max(np.array(image).shape[0], np.array(image).shape[1])
    image_resized = cv2.resize(np.array(image), dsize=(0, 0), fx=ratio, fy=ratio)            
    infer_helper = InferenceHelper(dataset='nyu')
    
    # predict depth of a single pillow image
    predicted_depth_resized = infer_helper.predict_pil(image_resized)
    predicted_depth = np.array(cv2.resize(predicted_depth_resized[0][0], dsize=np.transpose(np.zeros(np.array(image).shape[:-1]), (1, 0)).shape))

    layer = []
    depth_range = predicted_depth.max() - predicted_depth.min()
    sep = depth_range/split
    img_index = np.where(segmentation == label)
    depth_sum = 0
    for i in range(len(img_index[0])):
        depth_sum += predicted_depth[i][i]
    depth_mean = depth_sum/len(img_index[0])

    ### 포커싱 영역 마스크 저장
    label_mask = np.where(segmentation == label,1,0)
    label_mask = label_mask.astype(np.uint8)
    

    result_img = np.zeros(image.shape)
    ### split 수 만큼 depth별로 영역 나누기 = layer 
    ### 이미지 전체를 blur 처리 한 후에 해당 영역만 합성 진행
    ### 마지막 포커싱 영역 마스크 이용하여 이미지 합성
    for k in range(split+1):

        layer.append(np.where((predicted_depth >= predicted_depth.min()+sep*k) & (predicted_depth < predicted_depth.min()+sep*(k+1)),1,0))
        layer[k] = layer[k].astype(np.uint8)
        result_img = cv2.copyTo(cv2.GaussianBlur(image, (size, size), abs((k-int(predicted_depth.min()-depth_mean/sep))/15*blur_strength)), layer[k], result_img)
    result_img = cv2.copyTo(image, label_mask, result_img)
    
    Image.fromarray(result_img).save("blured_image.png")
