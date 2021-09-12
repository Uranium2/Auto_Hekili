from multiprocessing import Process

import PySimpleGUI as sg
from PIL import Image

from src.config import edit_config, load_config
from src.core import load_sources, process
from src.utils import (
    RectangleSelection,
    get_all_classes_specs,
    get_key_mapping,
    take_screenshot,
    update_key,
)


def set_process_state(is_running, window):
    window.Element("F3").Update(
        ("PAUSED", "RUNNING")[is_running],
        button_color=(("white", ("red", "green")[is_running])),
    )
    return is_running


def make_layout(config):
    class_spec = config["Class"]
    spells_key = get_key_mapping()[class_spec]
    col1 = [[sg.Text(f"{s}", key=f"ability_{s}")] for s in spells_key]
    col2 = [
        [sg.Input(f"{spells_key[s]}", key=f"{s}", enable_events=True)]
        for s in spells_key
    ]
    layout = [
        [
            [sg.Text("AUTO Hekili")],
            [
                sg.Combo(
                    get_all_classes_specs(),
                    default_value=class_spec,
                    enable_events=True,
                    key="Class",
                    readonly=True,
                )
            ],
            [sg.Button("Set Hekili spellbox square", key="-POS-")],
            [sg.Button("Run", key="F3")],
            [
                sg.Col(col1, k="-SPELL NAMES-"),
                sg.Col(col2, k="-BINDING-"),
            ],
        ]
    ]
    return layout


def make_window(config):
    window = sg.Window("Auto Hekili", make_layout(config), finalize=True, location=config["location"])
    window.bind("<Key-F3>", "F3")
    return window


def main_gui():
    config = load_config()
    # Create the window
    window = make_window(config)

    down_f3 = False
    p = None

    # Create an event loop
    while True:
        event, values = window.read()
        class_spec = values["Class"]
        print(class_spec)
        spells_key = get_key_mapping()[class_spec]
        imgs_src, file_names = load_sources(class_spec)
        spell_names = [f.split(".jpg")[0] for f in file_names]
        mapping = get_key_mapping()
        print(f"Event is : {event}")
        if event in spells_key.keys():
            print(values[event])
            mapping = update_key(class_spec, mapping, event, values[event])

        if event == "Exit" or event == sg.WIN_CLOSED:
            break
        if event == "-POS-":
            if p:
                p.terminate()
            down_f3 = set_process_state(False, window)
            img = Image.fromarray(take_screenshot(True))
            selector = RectangleSelection(img)
            while not selector.done:
                pass
            selector.close()
            edit_config("spellbox_rectangle", selector.rectangle, config)
        if event == "F3":
            down_f3 = set_process_state(not down_f3, window)
        if event == "Class":
            win_posX, win_posY = window.CurrentLocation()
            edit_config("location", (win_posX, win_posY), config)
            window.close()
            edit_config("Class", values["Class"], config)
            window = make_window(config)
        if down_f3:
            print("Starting process")
            print(config["spellbox_rectangle"])
            p = Process(
                target=process,
                args=(
                    1,
                    imgs_src,
                    spell_names,
                    spells_key,
                    config["spellbox_rectangle"],
                ),
            )
            p.start()
        else:
            if p:
                p.terminate()
    window.close()


if __name__ == "__main__":
    main_gui()
