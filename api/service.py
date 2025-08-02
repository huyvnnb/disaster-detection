from typing import List
from PIL.ImageFile import ImageFile
from ultralytics import YOLO

from api.schema import PredictResponse, Position

model = YOLO('model/baseline/best.pt')


class ProcessService:
    def inference(self, image: ImageFile) -> List[PredictResponse]:
        results = model.predict(image)[0]
        predicts = []
        for box in results.boxes:
            x1, y1, x2, y2 = box.xyxy[0].tolist()
            class_id = int(box.cls[0].item())
            class_name = results.names[class_id]
            conf = box.conf[0].item()

            position = Position(
                xmin=int(x1), ymin=int(y1), xmax=int(x2), ymax=int(y2)
            )
            predict = PredictResponse(
                position=position,
                class_id=class_id,
                class_name=class_name,
                confidence=conf
            )
            predicts.append(predict)
        return predicts


def get_process_service():
    return ProcessService()