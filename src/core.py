import sys
from os import listdir
from os.path import isfile, join

import cv2
import numpy as np
import pydirectinput
from PIL import Image

from src.utils import compare_imgs, crop_screenshot, take_screenshot


def load_sources(class_spec):
    mypath = f"img\\{class_spec}"
    file_names = [f for f in listdir(mypath) if isfile(join(mypath, f))]
    imgs_src = []
    for source_img_index in range(len(file_names)):
        img = np.asarray(Image.open(mypath + "\\" + file_names[source_img_index]))
        img = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        imgs_src.append(img)
    return imgs_src, file_names


def live_image_process(rectangle):
    x = rectangle[0]
    y = rectangle[1]
    h = rectangle[2]
    w = rectangle[3]

    img = take_screenshot(False)
    img = crop_screenshot(img, x, y, h, w)
    img = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    return img


def get_best_fit(img, imgs_src):
    min = sys.maxsize
    index = -1
    for i, img_src in enumerate(imgs_src):
        res = compare_imgs(img_src, img)
        # Save if pass treshold
        if res < min:  # and res < 8:
            min = res
            index = i
    return index


def batch_predict(batch_size, imgs_src, rectangle):
    indices = []
    for _ in range(batch_size):
        img = live_image_process(rectangle)
        indices.append(get_best_fit(img, imgs_src))
    return max(set(indices), key=indices.count)


def process(batch_size, imgs_src, spell_names, mapping, rectangle):
    while True:
        index = batch_predict(batch_size, imgs_src, rectangle)
        if index != -1:
            spell_name = spell_names[index]
            print(spell_name)
            key = mapping[spell_name]
            print(f"Pressing Key: {key}")
            pydirectinput.press(key, presses=3)
