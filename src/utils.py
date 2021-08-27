import json
import os
import re
from os import listdir
from os.path import isfile, join

import imagehash
import matplotlib.pyplot as plt
import numpy as np
import pyautogui
import pynput
import requests
from chromedriver_py import binary_path
from matplotlib.widgets import RectangleSelector
from PIL import Image
from pynput import mouse
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait


def crop_screenshot(img, x, y, h, w):
    return img[y : y + h, x : x + w]


def take_screenshot(pyautogui_default_color):
    img = np.array(pyautogui.screenshot())
    if pyautogui_default_color:
        return img
    return img[:, :, ::-1]


def compare_imgs(img_src, img):
    hash0 = imagehash.average_hash(Image.fromarray(img_src).resize(size=(100, 100)))
    hash1 = imagehash.average_hash(Image.fromarray(img).resize(size=(100, 100)))
    return hash0 - hash1


def show_compare(img_src, img):
    Image.fromarray(img_src).show()
    Image.fromarray(img).resize(size=(56, 56)).show()


def detect_click():
    with mouse.Events() as events:
        # Block at most one second
        event = ""
        while not isinstance(event, pynput.mouse.Events.Click):
            event = events.get()
        return True


class RectangleSelection(object):
    def __init__(self, img):
        self.rectangle = None
        self.img = img
        self.done = False

        # Setup the figure
        self.fig, self.ax = plt.subplots()
        self.fm = plt.get_current_fig_manager()
        plt.ion
        plt.title(
            "Draw a rectangle, using mouse, on Hekili spellbox. Press `q` to continue."
        )
        plt.imshow(self.img)
        manager = plt.get_current_fig_manager()
        manager.full_screen_toggle()
        plt.margins(0, 0)

        self.RS = RectangleSelector(
            self.ax,
            self.onselect,
            drawtype="box",
            useblit=True,
            button=[1, 3],
            minspanx=5,
            minspany=5,
            spancoords="pixels",
            interactive=True,
        )

        plt.connect("key_press_event", self.toggle_selector)
        plt.show()

    def onselect(self, e_click, e_release):
        x1, y1 = e_click.xdata, e_click.ydata
        x2, y2 = e_release.xdata, e_release.ydata
        print("(%3.2f, %3.2f) --> (%3.2f, %3.2f)" % (x1, y1, x2, y2))
        pt1 = (x1, y1)
        pt2 = (x2, y2)
        # calculate top left corner coords, width, height
        min_x = min(int(pt1[0]), int(pt2[0]))  # left
        min_y = min(int(pt1[1]), int(pt2[1]))  # top
        width = max(int(pt1[0]), int(pt2[0])) - min_x
        height = max(int(pt1[1]), int(pt2[1])) - min_y
        self.rectangle = (min_x, min_y, width, height)

    def toggle_selector(self, event):
        if event.key in ["Q", "q"] and self.RS.active:
            self.RS.set_active(False)
            self.done = True

    def close(self):
        # plt.show(block=False)
        plt.close()


def get_key_mapping():
    path = "config\\classes_spells.json"
    dict_ = {}
    if os.path.isfile(path):
        with open(path, "r") as f:
            dict_ = json.load(f)
    else:
        classes_specs = get_all_classes_specs()
        create_key_mapping(classes_specs)
    return dict_


def update_key(class_spec, mapping, spell, key):
    mapping[class_spec][spell] = key
    path = "config\\classes_spells.json"
    with open(path, "w") as outfile:
        json.dump(mapping, outfile, indent=4, sort_keys=True)
    return mapping


def create_key_mapping(classes_specs):
    dict_ = {}
    for class_spec in classes_specs:
        dict_[class_spec] = dict.fromkeys(get_spells_from_class_spec(class_spec), "")

    path = "config\\classes_spells.json"
    if not os.path.isfile(path):
        with open(path, "w+") as outfile:
            json.dump(dict_, outfile, indent=4, sort_keys=True)
    return dict_


def edit_spell_list(spells, spells_to_add, spells_to_replace):
    spells_ = set(spells)

    if spells_to_add:
        for s in spells_to_add:
            spells_.add(s)

    if spells_to_replace:
        for k in spells_to_replace:
            spells_.remove(k)
            if spells_to_replace[k] != "":
                spells_.add(spells_to_replace[k])
    return spells_


def get_spells_from_class_spec(class_spec):
    spells = []
    with open(f"config\\Notes\\90_{class_spec}.simc") as f:
        for line in f:
            match_equal = re.search("actions=[a-z_]*", line)
            match = re.search("=/[a-z_]*", line)
            if match:
                spells.append(match.group().split("=/")[-1])
            if match_equal:
                spells.append(match_equal.group().split("actions=")[-1])

        if class_spec == "Death_Knight_Unholy":
            spells = edit_spell_list(
                spells, ["scourge_strike"], {"wound_spender": "clawing_shadows"}
            )
        if class_spec == "Druid_Balance":
            spells = edit_spell_list(spells, None, None)
        if class_spec == "Druid_Feral":
            spells = edit_spell_list(spells, None, {"thrash_cat": "thrash"})
        if class_spec == "Druid_Guardian":
            spells = edit_spell_list(
                spells,
                None,
                {"thrash_bear": "thrash", "berserk_bear": "berserk"},
            )
        if class_spec == "Mage_Arcane":
            spells = edit_spell_list(spells, None, {"use_mana_gem": ""})
        if class_spec == "Rogue_Subtlety":
            spells = edit_spell_list(spells, None, {"apply_poison": ""})
        if class_spec == "Warlock_Destruction":
            spells = edit_spell_list(spells, None, {"blood_of_the_enemy": ""})
        if class_spec == "Hunter_Marksmanship":
            spells = edit_spell_list(spells, None, {"multishot": "multi-shot"})
        if class_spec == "Hunter_BeastMastery":
            spells = edit_spell_list(spells, None, {"multishot": "multi-shot"})

    spells = set(spells)
    values_to_remove = [
        "call_action_list",
        "cancel_buff",
        "use_items",
        "use_item",
        "run_action_list",
        "variable",
        "wait",
        "potion",
        "any_dnd",
        "trinket",
        "sequence",
        "retarget_auto_attack",
        "bottled_flayedwing_toxin",
        "pool_resource",
        "swipe_cat",
        "swipe_bear",
        "wrathstone",
    ]
    for val in values_to_remove:
        if val in spells:
            spells.remove(val)
    spells = list(spells)
    spells.sort()
    return spells


def get_all_classes_specs():
    mypath = "config\\Notes"
    file_names = [
        f.replace("90_", "").replace(".simc", "")
        for f in listdir(mypath)
        if isfile(join(mypath, f))
    ]
    file_names.sort()
    return file_names


def scrap_and_save_icons():
    path = "config\\classes_spells.json"
    with open(path, "r") as outfile:
        dict_ = json.load(outfile)

    chrome_options = Options()
    chrome_options.add_argument("--headless")
    driver = webdriver.Chrome(executable_path=binary_path, options=chrome_options)

    root_path = "img"
    for class_ in dict_:
        path = root_path + "\\" + class_

        for spell in dict_[class_]:
            print(spell)
            spell_research = spell.replace("_", "+")
            base_url = f"https://www.wowhead.com/spells/name:{spell_research}"
            driver.get(base_url)
            WebDriverWait(driver, 1)
            # print(driver.page_source)
            url_spell = re.findall(
                f"""/spell=[0-9]*/{spell.lower().replace("_", "-")}">""",
                str(driver.page_source),
            )[0].split('">')[0]
            print(url_spell)

            driver.get(f"https://www.wowhead.com{url_spell}")
            WebDriverWait(driver, 1)
            url = re.search(
                "https://wow.zamimg.com/images/wow/icons/large/[a-zA-Z0-9_]*.jpg",
                driver.page_source,
            ).group()

            r = requests.get(url, allow_redirects=True)
            print(url)

            path_file = path + "\\" + spell + ".jpg"
            os.makedirs(os.path.dirname(path_file), exist_ok=True)
            with open(path_file, "wb") as f:
                f.write(r.content)
