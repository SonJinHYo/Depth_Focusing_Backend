import torch
from PIL import Image, ImageOps
import numpy as np
import requests
from transformers import AutoImageProcessor, Mask2FormerForUniversalSegmentation
from collections import defaultdict
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib import cm


def predict_segmentation(img_url):
    image = Image.open(requests.get(img_url, stream=True).raw)
    image = ImageOps.exif_transpose(image) # 이미지 업로드시 회전되는 문제 해결
    image = Image.fromarray(np.array(image)[:,:,0:3])
    processor = AutoImageProcessor.from_pretrained(
        "facebook/mask2former-swin-base-coco-panoptic"
    )
    model = Mask2FormerForUniversalSegmentation.from_pretrained(
        "facebook/mask2former-swin-base-coco-panoptic"
    )

    inputs = processor(image, return_tensors="pt")

    with torch.no_grad():
        outputs = model(**inputs)

    predicted_segmentation = processor.post_process_panoptic_segmentation(
        outputs, target_sizes=[image.size[::-1]]
    )[0]
    predicted_segmentation["segmentation"] = np.array(predicted_segmentation['segmentation'])

    return (
        predicted_segmentation["segmentation"],
        predicted_segmentation["segments_info"],
        model,
    )


def draw_panoptic_segmentation(model, segmentation, segments_info):
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
        "segmentation.png",
        format="png",
    )
