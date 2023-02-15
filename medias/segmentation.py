import torch
from PIL import Image, ImageOps
import numpy as np
import requests
import cv2
from transformers import AutoImageProcessor, Mask2FormerForUniversalSegmentation
from collections import defaultdict
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib import cm


def predict_segmentation(img_url):
    image = Image.open(requests.get(img_url, stream=True).raw)
    image = ImageOps.exif_transpose(image)  # 이미지 업로드시 회전되는 문제 해결
    image = Image.fromarray(np.array(image)[:, :, 0:3])
    ratio = 640 / max(np.array(image).shape[0], np.array(image).shape[1])
    image_resized = cv2.resize(np.array(image), dsize=(0, 0), fx=ratio, fy=ratio)
    print("image_resized ok")
    processor = AutoImageProcessor.from_pretrained(
        "facebook/mask2former-swin-base-coco-panoptic"
    )
    model = Mask2FormerForUniversalSegmentation.from_pretrained(
        "facebook/mask2former-swin-base-coco-panoptic"
    )

    inputs = processor(image_resized, return_tensors="pt")

    with torch.no_grad():
        outputs = model(**inputs)

    predicted_segmentation = processor.post_process_panoptic_segmentation(
        outputs, target_sizes=[image_resized.size[::-1]]
    )[0]

    segmentation = np.array(
        cv2.resize(
            predicted_segmentation["segmentation"][0][0],
            dsize=np.transpose(np.zeros(np.array(image).shape[:-1]), (1, 0)).shape,
        )
    )
    print("image_back_resized ok")
    # predicted_segmentation["segmentation"] = np.array(
    #     predicted_segmentation["segmentation"]
    # )

    return (
        segmentation,
        predicted_segmentation["segments_info"],
        model,
    )


def draw_panoptic_segmentation(model, segmentation, segments_info, pk):
    # get the used color map
    viridis = cm.get_cmap("viridis", torch.max(segmentation))
    fig, ax = plt.subplots()
    ax.imshow(segmentation)

    ### legend (this part will be edited depending on web environment)
    instances_counter = defaultdict(int)
    handles = []
    # for each segment, draw its legend
    num = 1
    for segment in segments_info:
        segment_id = segment["id"]
        segment_label_id = segment["label_id"]
        segment_label = model.config.id2label[segment_label_id]
        label = f"{num}. {segment_label}-{instances_counter[segment_label_id]}"
        instances_counter[segment_label_id] += 1
        color = viridis(segment_id - 1)
        handles.append(mpatches.Patch(color=color, label=label))
        num += 1
    ax.legend(handles=handles, loc="center left", bbox_to_anchor=(1, 0.5))

    plt.axis("off")
    plt.savefig(
        f"tmp/segmentation_{pk}.png",
        format="png",bbox_inches = 'tight',
    )
