from pathlib import Path
from typing import Union, List

import cv2
import torch
from numpy.typing import NDArray

from constants import DATA_DIR, WEIGHTS_DIR
from src.base import BasePredictor, DetectionCoal
from src.utils import get_device, get_yolov5


class YOLOv5(BasePredictor):

    def __init__(
            self,
            weights: Union[Path, str],
            box_conf_th: float = 0.5,
            nms_th: float = 0.2,
            amp: bool = True,
            size: int = 1280,
            device: str = None,
    ):
        self.device = get_device(device=device)
        self.model = get_yolov5(
            weights=weights,
            box_conf_th=box_conf_th,
            nms_th=nms_th,
            amp=amp,
            device=self.device
        )
        self.size = size

    @torch.no_grad()
    def predict(self, img: NDArray) -> List[DetectionCoal]:
        prediction = self.model(img, size=self.size)
        boxes = prediction.xyxy[0].detach().cpu().numpy()
        return [DetectionCoal(box[:4]) for box in boxes]


if __name__ == '__main__':
    image = cv2.imread(str(DATA_DIR / 'few_data_split' / 'few_data_train' / '20210712_141048_857A_ACCC8EAF31F3_0.jpg'))
    yolo = YOLOv5(
        weights=WEIGHTS_DIR / 'yolov5n6.pt',
        box_conf_th=0.2,
        nms_th=0.2,
        amp=True,
        size=1280,
        device=None
    )

    coals = yolo.predict(image[..., ::-1])
    print([coal.get_fraction() for coal in coals])

    if coals:
        cv2.imshow('Contours', coals[0].plot_on(image))
        cv2.waitKey(0)
        cv2.destroyAllWindows()
