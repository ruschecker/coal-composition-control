import cv2
import numpy as np
import segmentation_models_pytorch as smp
import torch


def get_device(device: str):
    if device is None:
        return torch.device('cuda') if torch.cuda.is_available() else torch.device('cpu')
    return torch.device(device)


def get_mask_rcnn(weights, box_conf_th: float, nms_th: float, device):
    model = torch.load(weights, map_location=device)
    model.roi_heads.score_thresh = box_conf_th
    model.roi_heads.nms_thresh = nms_th
    model.eval()
    return model


def get_unet(weights, device):

    CLASSES = ['coal', 'bound', 'background']
    model = smp.Unet(
        encoder_name='efficientnet-b0',
        encoder_weights='imagenet',
        classes=len(CLASSES),
        activation='softmax',
    )
    model_state_dict = torch.load(weights, map_location=device)
    model.load_state_dict(model_state_dict)
    model = model.to(device)
    model.eval()
    return model


def get_contours(mask):
    contours, _ = cv2.findContours(mask,  cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)
    return contours


def visualize_semantic_segmentation(img_from_camera, pred):
    return np.where(
        pred > 240,
        cv2.addWeighted(img_from_camera, 0.4, pred, 0.6, 1.0),
        img_from_camera,
    )


def plot_coals_contours_on_img(img, coals: list):
    img_with_contours = np.copy(img)
    for coal2plot in coals:
        coal2plot.plot_on(img_with_contours)
    return img_with_contours
