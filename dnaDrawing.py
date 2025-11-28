# taking frames from a video then using 'A', 'T', 'C', and 'G' to redraw them
# deciding which base based on luminance 
# luminance = 0.2126r + 0.7152g + 0.0722b   https://www.itu.int/dms_pubrec/itu-r/rec/bt/R-REC-BT.709-6-201506-I!!PDF-E.pdf
# 'T' = 0-60
# 'C' = 60-125
# 'A' = 125-190
# 'G' = 190-255

import numpy as np
import cv2


def drawWithDna(inputName):
    # getting original video info
    cap = cv2.VideoCapture(inputName)

    while True:
        ret, frame = cap.read()
        if not ret:
            break
        newFrame = ""
        for row in frame:
            for pixel in row:
                luminance = 0.2126 * pixel[0] + 0.7152 * pixel[1] + 0.0722 * pixel[2]
                if luminance > 190:
                    newFrame += 'G'
                elif luminance > 125:
                    newFrame += 'A'
                elif luminance > 60:
                    newFrame += 'C'
                else:
                    newFrame += 'T'
            newFrame += '\n'
        print(newFrame)
    
    cap.release()
    return

# print(drawWithDna('original-videos/food.mp4'))
# print(drawWithDna('original-videos/bad_apple.mp4'))

# ffmpeg -i 'food_terminal.mov' -filter:v "setpts=PTS/33" -an "food_dna_drawing.mp4"
# ffmpeg -i 'bad_apple_terminal.mov' -filter:v "setpts=PTS/5.6" -an "bad_apple_dna_drawing.mp4"