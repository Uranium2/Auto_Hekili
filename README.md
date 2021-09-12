# AUTO_Hekili (WIP)

AUTO_Hekili is a program that will attempt to read the [Hekili](https://github.com/Hekili/hekili) in-game main icon, and send a keystroke regarding to this spell.


# Disclaimer 

This project has no mean to be efficient or to replace your brain while you play.

This program is surely against ToS of World of Warcraft since it is sending keyboard keys.

I do not take any responsibility for any account bans.

## How to setup :

* Setup first the project:

    * Be sure to have Python 3 installed on your OS.

        ```shell
        $> git clone https://github.com/Uranium2/Auto_Hekili
        $> cd Auto_Hekili
        $> python3 -m venv .venv
        $> .venv\Scripts\activate
        (.venv) $> pip3 install -r requirements.txt
        ```

    * To launch :

        ```shell
        (.venv) $> python3 main.py
        ```

* Setup Auto_Hekili :

    * You need to set Hekili spellbox location on your screen. For this, press `Set Hekili spellbox square`, and then click and drag your mouse over the Hekili spellbox. Once placed, you can quit the screenshot by pressing `q`.

    * Then you have to select your class and specialisation in the dropdown list.

    * Finally you should assign your key bindings next to each spells in the spell list. Your bindings needs to match the ones you have sent inside World of Warcraft. Else it will press on an other spell in your client.

    * Press `F3` to toggle on or off the prediction. Make sure to select World of Warcraft game client. Else it will send keys to wherever you pressed.

    * __Be aware.__ If you press `ENTER` in game, it will send keys in the chat.
