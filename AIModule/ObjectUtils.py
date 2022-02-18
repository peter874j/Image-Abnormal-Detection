from dataclasses import dataclass

@dataclass
class Point2D:
    x: int
    y: int

class BBox:

    def __init__(self, zoneName, startPoint, endPoint, centerPoint):
        self.zoneName = zoneName
        self.startPoint = startPoint
        self.endPoint = endPoint
        self.centerPoint = centerPoint

    @classmethod
    def get_from_list(cls, zoneName, startPointX, startPointY, endPointX, endPointY):
        centerPointX = int((startPointX + endPointX)/2)
        centerPointY = int((startPointY + endPointY)/2)
        return cls(zoneName, Point2D(startPointX, startPointY), Point2D(endPointX, endPointY), Point2D(centerPointX, centerPointY))

    def contains_point(self, point):
        if self.startPoint.x > point.x or self.endPoint.x < point.x:
            return False
        if self.startPoint.y > point.y or self.endPoint.y < point.y:
            return False
        return True  

class Zone:
    A = "Placement"
    B = "Jig"
    C = "Work_Rack"
    D = "Finish"

class Label:
    type1 = "no_PCB"
    type2 = "PCB_frame"
    type3 = "frame"
    order = [type1, type2, type3, type2, type1]

    def __init__(self, previous, current):
        self.previous = previous
        self.current = current

    @classmethod
    def initialize(cls):
        return cls(cls.type1, cls.type1)

    def is_not_same_label(self, step):
        if self.previous == step.previousLabel and self.current == step.currentLabel:
            return "NO"
        else:
            return "YES"  

    def get_Jig_label(self, yoloResult, allRectangleInfo):
        if len(yoloResult["coordinate"]) == 1:
            if allRectangleInfo[1].contains_point(yoloResult["coordinate"][0].centerPoint): ##########要改 1
                return yoloResult["label"][0]
        return None
    
    def update_info(self, yoloResult, allRectangleInfo):
        self.previous = self.current
        jigCurrentLabel = self.get_Jig_label(yoloResult, allRectangleInfo)
        self.current = jigCurrentLabel if jigCurrentLabel is not None else self.current

class Step:
    def __init__(self, number, label):
        self.number = number
        self.previousLabel = label.previous
        self.currentLabel = label.current

    @classmethod
    def initialize(cls):
        return cls(0, Label.initialize())

    def update_info(self):
        self.number += 1 
        self.previousLabel = Label.order[self.number-1]
        self.currentLabel = Label.order[self.number]

    @staticmethod
    def goto_next(jigLabel):
        if not jigLabel.previous == jigLabel.current:
            return True

