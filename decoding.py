###
# Decoding:
#       Takes in DNA, rounding parameter (to know how to decode), and "mutation" (recessive, sickle, cancer, RIP, ...)
#           Recessive - 25% chance for previous pixel to remain
#           Sickle - GAG --> GTG, CTC --> CAC https://pmc.ncbi.nlm.nih.gov/articles/PMC7510211/
#           Cancer - 10% chance for pixels next to starting empty pixel to become empty as well
#           RIP - C --> T when a pixel is the same as the previous one https://pmc.ncbi.nlm.nih.gov/articles/PMC1451165/
#           ...
#       Get fps and frame size (m, n)
#       for every m * n pixels:
#           initialize image with frame size
#           decode each pixel in each frame
#           write pixel to image
#       concat images to video with same fps
#       return video 
# ###

import cv2
import numpy as np

decodingDict = {
    'A': 0,
    'T': 1,
    'C': 2,
    'G': 3
}

# converts base 4 --> num
# where A = 0, T = 1, C = 2, G = 3
def fromBases(sequence):
    num = 0
    for i in range(0, len(sequence)):
        num += decodingDict[sequence[i]] * (4 ** (len(sequence) - i - 1))
    return num


def highDecoding(sequence):
    pixels = []
    for s in sequence:
        if s == 'A' or s == 'C':
            pixels.append([0, 0, 0])
        else:
            pixels.append([255, 255, 255])
    return pixels


medDecodingDict = {
    'AC': 0,
    'GT': 50,
    'TC': 100,
    'GA': 150,
    'CG': 200,
    'AT': 250
 }   


def medDecoding(sequence):
    pixels = []
    for c in range(0, len(sequence), 2):
        pixels.append(medDecodingDict[sequence[c:c+2]])
    return np.array(pixels).reshape(-1, 3)


def lowDecoding(sequence):
    pixels = []
    for c in range(0, len(sequence), 3):
        pixels.append(fromBases(sequence[c:c+3]) * 5)
    return np.array(pixels).reshape(-1, 3)


def noneDecoding(sequence):
    pixels = []
    for c in range(0, len(sequence), 4):
        pixels.append(fromBases(sequence[c:c+4]))
    return np.array(pixels).reshape(-1, 3)
        


def decodeDNA(encodedFile, outputPath, mutation='none'):
    with open(encodedFile, 'r') as f:
        dna = f.read()
        # getting posterization
        pBase = dna[0]
        if pBase == 'A':
            posterization = 'high'
        elif pBase == 'T':
            posterization = 'med'
        elif pBase == 'C':
            posterization = 'low'
        else:
            posterization = 'none'
        # getting info
        fps = fromBases(dna[1:5])
        width = fromBases(dna[5:11])
        height = fromBases(dna[11:17])
        # setting up video
        fourcc = cv2.VideoWriter_fourcc(*'MJPG')
        out_filename = outputPath + '.avi'
        fps = float(fps)
        vid = cv2.VideoWriter(out_filename, fourcc, fps, (width, height))
        # now getting the frames
        i = 17
        frame = [] # starting with the frame being flat
        frameSize = width * height
        prevFrame = None
        frameCount = 0
        while i < len(dna):
            # first frame
            if prevFrame is None:
                if posterization == 'high':
                    frame = highDecoding(dna[i: i + frameSize])
                    i += frameSize
                elif posterization == 'med':
                    # 3 colors per pixel, 2 bases per color
                    frame = medDecoding(dna[i: i + (frameSize * 6)])
                    i += frameSize * 6
                elif posterization == 'low':
                    # 3 colors per pixel, 3 bases per color
                    frame = lowDecoding(dna[i : i + (frameSize * 9)])
                    i += frameSize * 9
                else: # no posterization
                    # 3 colors per pixel, 4 bases per color
                    frame = noneDecoding(dna[i: i + (frameSize * 12)])
                    i += frameSize * 12
            # rest of frames - check for run-length encoding
            else:
                # run-length encoding
                if dna[i] == 'G':
                    i += 1
                    # next two bases give run length
                    runLength = fromBases(dna[i:i+2])
                    i += 2
                    for run in range(0, runLength):
                        pixelIndex = len(frame)
                        frame.append(prevFrame[pixelIndex])
                # change from prev frame
                else:
                    i += 1 # 'C'
                    if posterization == 'high':
                        for pixel in highDecoding(dna[i]):
                            frame.append(pixel)
                        i += 1
                    elif posterization == 'med':
                        for pixel in medDecoding(dna[i: i+6]):
                            frame.append(pixel)
                        i += 6
                    elif posterization == 'low':
                        for pixel in lowDecoding(dna[i: i+9]):
                            frame.append(pixel)
                        i += 9
                    else: # no posterization
                        for pixel in noneDecoding(dna[i: i+12]):
                            frame.append(pixel)
                        i += 12
            if len(frame) == frameSize:
                # write to video
                reshapedFrame = np.array(frame).reshape(height, width, 3)
                vid.write(reshapedFrame.astype(np.uint8))
                prevFrame = frame
                frame = []
                frameCount += 1
                if frameCount % 10 == 0:
                    print(f"Wrote frame {frameCount}")
        vid.release()
        print(f"All frames completed! Video at {out_filename}")
    return out_filename
        

# decodeDNA("dna-encodings/bad_apple.mp4_high_encoding.txt", "decoded-videos/bad_apple_high_none", "none")
# decodeDNA("dna-encodings/bad_apple.mp4_med_encoding.txt", "decoded-videos/bad_apple_med_none", "none")
# decodeDNA("dna-encodings/bad_apple.mp4_low_encoding.txt", "decoded-videos/bad_apple_low_none", "none")
# decodeDNA("dna-encodings/bad_apple.mp4_none_encoding.txt", "decoded-videos/bad_apple_none_none", "none")
decodeDNA("dna-encodings/food.mp4_high_encoding.txt", "decoded-videos/food_high_none", "none")
decodeDNA("dna-encodings/food.mp4_med_encoding.txt", "decoded-videos/food_med_none", "none")
decodeDNA("dna-encodings/food.mp4_low_encoding.txt", "decoded-videos/food_low_none", "none")
decodeDNA("dna-encodings/food.mp4_none_encoding.txt", "decoded-videos/food_none_none", "none")
