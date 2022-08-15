from time import sleep
import numpy as np
import cupy as cp
import cv2

from PIL import Image, ImageFilter
import matplotlib.pyplot as plt
from IPython.display import clear_output


def capturenow(net,pattern):
    #param is the index of the video captureing device to be used
    cap = cv2.VideoCapture(2)
    i = 0

    while(True):

        ret, frame = cap.read()

        input_img = processframe(frame, i)

        # process only every 32th frame
        if i % 32 == 0:
            cp_img = cp.array(input_img)
            fwd = net.feedforward(cp_img)
            # Print the prediction of the network
            print(str(np.round(fwd, 2)).replace("\n",""))
            print('Network prediction: ' + str(cp.argmax(fwd)) + '\n')

            net.evaluate_src_pattern(pattern,cp_img)

            input_img = input_img.reshape((28, 28))

            plt.imshow(input_img)
            plt.show()
            sleep(0.1)
            clear_output(wait=True)

        # break loop if q is pressed
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break
        i += 1

    # When done, release the capture
    cap.release()
    cv2.destroyAllWindows()

def processframe(frame, i):
    frame_grey = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    cv2.resize(frame_grey, [560, 560], interpolation=cv2.INTER_CUBIC)
    cv2.imshow('Camera', frame_grey)

    if i % 32 == 0:

        img = Image.fromarray(frame_grey)
        new_image = Image.new('L', (28, 28), (255))

        img = img.resize((28, 28), Image.ANTIALIAS).filter(ImageFilter.SHARPEN)
        new_image.paste(img)

        tv = list(new_image.getdata())

        # normalize pixels
        input_img = [(255 - x) * 1.0 / 255.0 for x in tv]

        input_img = np.array(input_img)

        def filter_treshhold(pixel):
            if pixel < .5:
                return 0
            return pixel

        
        input_img = np.array(list(map(filter_treshhold, input_img)))

        #serialize the data so that it can be processed by the network with dot products
        input_img = np.reshape(input_img, (input_img.size, 1))

        return input_img
