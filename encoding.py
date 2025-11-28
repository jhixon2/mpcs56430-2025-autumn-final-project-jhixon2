###
#     Encoding:
#       Takes in a video and parameter for rounding colors (None, Low, Medium, High)
#           None - keeps colors as are
#           Low - rounds to nearest multiple of 5
#           Medium - rounds to nearest multiple of 50
#           High - black and white
#       Get frames and fps
#       Get size of frame
#       Get pixels
#       Determine color-->pixel encoding to use based on rounding parameter
#       Initialize DNA
#       Write fps to DNA
#       Write frame size to DNA
#       Write out first frame's pixels to DNA
#       For each frame, for each pixel
#           if same as previous, write G to DNA
#           else write C, then new colors to DNA
#       return DNA 
###

import random
import numpy as np
import cv2
import os


# Encoding schemes

encodingDict = {
    0: 'A',
    1: 'T',
    2: 'C',
    3: 'G'
}
def toBases(num, pad):
    baseFour = np.base_repr(num, base=4)
    encodedNum = ""
    i = 0
    while i < pad - len(baseFour):
        encodedNum += 'A'
        i += 1
    for n in baseFour:
        encodedNum += encodingDict[int(n)]
    return encodedNum

# High (black and white)
    # for 0 choose at random A or C
    # for 255 choose at random T or G
def highEncoding(color):
    if color == 0:
        return random.choice(['A', 'C'])
    return random.choice(['T', 'G'])

# Medium (0, 50, 100, 150, 200, 250)
medEncoding = {
    0: 'AC',
    50: 'GT',
    100: 'TC',
    150: 'GA',
    200: 'CG',
    250: 'AT'
}

# Low (multiples of 5 --> 52 possibilities)
    # need 3 bases to encode since 4^3 > 52
    # divide the color by 5 (0 --> 0, 5 --> 1, ..., 250-->50, 255-->51)
    # write that number with 3 bases, A = 0, T = 1, C = 2, G = 3
# toBases(num / 5, 3)
lowEncodingTable = {i: toBases(i / 5, 3) for i in range(0, 256, 5)}

# None (0-255 --> 256 possibilities)
    # need 4 bases to encode since 4^4 = 256
    # write the color with 4 bases, A = 0, T = 1, C = 2, G = 3
# toBases(num, 4)
noneEncodingTable = {i: toBases(i, 4) for i in range(0, 256)}


# posterization
    # high: rounding to 0, 255
    # medium rounding to 50's
    # low rounding to 5's
medPosterizationTable = (np.round(np.arange(0, 256) / 50) * 50).astype(np.uint8)
lowPosterizationTable = (np.round(np.arange(0, 256) / 5) * 5).astype(np.uint8)


# Encoding
# A = 0, T = 1, C = 2, G = 3
def encodeFrames(frame, prevFrame, posterization):
    # posterization
    if posterization == 'high':
        frame = ((frame >= 127) * 255)
    elif posterization == 'med':
        frame = medPosterizationTable[frame].astype(np.uint8)
    elif posterization == 'low':
        frame = lowPosterizationTable[frame].astype(np.uint8)
    # encoding
    encodedFrame = []
    if prevFrame is not None:
        samePixels = np.all(frame == prevFrame, axis=2)
        allPixels = frame.reshape(-1, 3)
        samePixels = samePixels.flatten()
        p = 0
        while p < len(allPixels):
            # same --> run length encoding
            if samePixels[p]:
                runLength = 1
                # setting max run length to 15, so that only 2 bases are needed to encode it
                while runLength < 15 and p + runLength < len(allPixels) - 1 and samePixels[p + runLength]:
                    runLength += 1
                p += runLength - 1
                encodedFrame.append('G')
                encodedFrame.append(toBases(runLength, 2))
            else:
                encodedFrame.append('C')
                pixel = allPixels[p]
                if posterization == 'high':
                    encodedFrame.append(highEncoding(pixel[0]))
                elif posterization == 'med':
                    encodedFrame.append(medEncoding[pixel[0]])
                    encodedFrame.append(medEncoding[pixel[1]])
                    encodedFrame.append(medEncoding[pixel[2]])
                elif posterization == 'low':
                    encodedFrame.append(toBases(pixel[0] / 5, 3))
                    encodedFrame.append(toBases(pixel[1] / 5, 3))
                    encodedFrame.append(toBases(pixel[2] / 5, 3))
                else:
                    encodedFrame.append(toBases(pixel[0], 4))
                    encodedFrame.append(toBases(pixel[1], 4))
                    encodedFrame.append(toBases(pixel[2], 4))
            p += 1
    else:
        # first frame
        for pixel in frame.reshape(-1, 3):
                if posterization == 'high':
                    encodedFrame.append(highEncoding(pixel[0]))
                elif posterization == 'med':
                    encodedFrame.append(medEncoding[pixel[0]])
                    encodedFrame.append(medEncoding[pixel[1]])
                    encodedFrame.append(medEncoding[pixel[2]])
                elif posterization == 'low':
                    encodedFrame.append(toBases(pixel[0] / 5, 3))
                    encodedFrame.append(toBases(pixel[1] / 5, 3))
                    encodedFrame.append(toBases(pixel[2] / 5, 3))
                else:
                    encodedFrame.append(toBases(pixel[0], 4))
                    encodedFrame.append(toBases(pixel[1], 4))
                    encodedFrame.append(toBases(pixel[2], 4))
    return ''.join(encodedFrame), frame
                

# Main function
def vidToDna(videoPath, posterization='none'):
    # get fps, width, and height
    cap = cv2.VideoCapture(videoPath)
    fps = int(cap.get(cv2.CAP_PROP_FPS))
    width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    frameCount = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))

    videoName = videoPath.split('/')[-1]
    with open(f"dna-encodings/{videoName}_{posterization}_encoding.txt", 'w') as f:
        # 1 base needed to write out which posterization
        if posterization == 'high':
            f.write('A')
        elif posterization == 'med':
            f.write('T')
        elif posterization == 'low':
            f.write('C')
        else: # No posterization
            f.write('G')
        # assuming fps <= 240, we need 4 bases to encode >= 240 (4^4 = 256)
        f.write(toBases(fps, 4))
        # assuming no videos of resolution greater than 4k, the largest possible frame size is 3840x2160 pixels
        # in base 4, we need 6 bases to encode >= 3840 (4^6 = 4096)
        f.write(toBases(width, 6))
        f.write(toBases(height, 6))

        prevFrame = None
        i = 0
        while True:
            ret, frame = cap.read()
            if not ret:
                break
            encodedFrame, prevFrame = encodeFrames(frame, prevFrame, posterization)
            f.write(encodedFrame)
            i += 1
            if i % 10 == 0:
                print(f"Frame {i} / {frameCount} done")

    cap.release()
    print(f'Encoding complete. Find it in dna-encodings/{videoName}_{posterization}_encoding.txt')


# vidToDna("original-videos/bad_apple.mp4", 'high')
# vidToDna("original-videos/bad_apple.mp4", 'med')
# vidToDna("original-videos/bad_apple.mp4", 'low')
# vidToDna("original-videos/bad_apple.mp4")
vidToDna("original-videos/food.mp4", 'high')
vidToDna("original-videos/food.mp4", 'med')
vidToDna("original-videos/food.mp4", 'low')
vidToDna("original-videos/food.mp4")
