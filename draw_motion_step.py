import cv2
import numpy as np

def draw_step(img, stateDict, isAnomalyStep, numOfCurrentStep, lineThickness=3):
    
    ### initial parameter
    (imgH, imgW, ch) = img.shape
    result = {'step_result':isAnomalyStep, 'step_num':numOfCurrentStep}
    color ={-1:[0, 0 ,255], 0:[125, 125 ,125], 1:[0, 255, 0]}   # -1:red, 0:gray, 1:green 
    stepImg = np.full(shape=(imgH, imgW/2, ch), fill_value=[255, 255, 255], dtype=np.uint8)   # background for step flow display
    stepText = ["Start", "Step1. Work_Rack to Jig", "Step2. Jig to Finish", "Step3. Placement to Jig", "Step4. Jig to Work_Rack", "End"]
    (stepImgH, stepImgW, _) = stepImg.shape

    ### judge the step of motion result
    for i in range(len(result['step_num'])):
        ### define all step state
        if result['step_num'] == '0':   # step End
            stateDict['end'] += 1
        
        if result['step_num'] == '1':   # step Start
            stateDict['start'] += 1
        
        if result['step_num'] == '4':   # reset
            stateDict['start'] = 0
            stateDict['end'] = 0
            stateDict['1'] = 0
            stateDict['2'] = 0
            stateDict['3'] = 0
            stateDict['4'] = 0
        
        if result['step_result'][i] == "NO":   # step OK
            stateDict[str(i)] += 1
        
        elif result['step_result'][i] == "YES":   # step NG
            stateDict[str(i)] -= 1

    ### update text
    tl = lineThickness or round(0.002 * (stepImgH + stepImgW) / 2) + 1  # line/font thickness
    textGap = stepImgH / (len(stepText) + 1)  
    stateValues = stateDict.values()
    valuesList = list(stateValues)
    for i, text in enumerate(stepText):
        textSize = cv2.getTextSize(text, 0, fontScale=tl / 3, thickness=2)[0]
        xCoords = int(0.5 * stepImgW - 0.5 * textSize[0])
        yCoords = textSize[1] * (i+1) + textGap * (i+1)
        cv2.putText(stepImg, text, (xCoords, yCoords), 0, tl / 3, color[valuesList[i]], thickness=2, lineType=cv2.LINE_AA)
    
    drawImg = cv2.hstack([img, stepImg])

    return drawImg

if __name__ == '__main__':

    stateDict = {'start':0, '1':0, '2':0, '3':0, '4':0, 'end':0}   # 0:default, 1:OK, -1:NG
    rawImg = cv2.imread('motion_frame.jpg')
    isAnomalyStep = [str0, str1, str2, str3, str4]   # YES/NO
    numOfCurrentStep = [0, 1, 2, 3, 4]   # 0~4
    outImg = draw_step(rawImg, stateDict, isAnomalyStep, numOfCurrentStep)
