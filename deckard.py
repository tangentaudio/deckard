#!/bin/sh
"exec" "`dirname $0`/.venv/bin/python" "$0" "$@"
# ^^ this shebang should run the venv python that was created
#    in the deckard directory during the installation

###############################################################
#
#   __| | ___  ___| | ____ _ _ __ __| |
#  / _` |/ _ \/ __| |/ / _` | '__/ _` |
# | (_| |  __/ (__|   < (_| | | | (_| |
#  \__,_|\___|\___|_|\_\__,_|_|  \__,_|
#
# Deckard provides StreamDeck support for LinuxCNC
#
# Copyright (c) 2024 Steve Richardson
# https://github.com/tangentaudio/deckard
#
###############################################################

import os
import hal
import threading
import argparse
import configparser
from enum import Enum
from PIL import Image, ImageDraw, ImageFont, ImageFilter
from StreamDeck.DeviceManager import DeviceManager
from StreamDeck.ImageHelpers import PILHelper
from StreamDeck.Transport.Transport import TransportError

ASSETS_PATH = os.path.join(os.path.dirname(__file__), "assets")
HAL = hal.component("deckard")

class KeyTypes(Enum):
    UNUSED = 0
    MOMENTARY = 1
    TOGGLE = 2
    TOGGLE2 = 3

class Key:
    def __init__(self, deckref, halref, confref, id):
        self.deck = deckref
        self.hal = halref
        self.config = confref
        self.configopts = {}
        self.id = id

        conf_section = "key.{:02}".format(self.id)
        if conf_section in self.config.sections():
            self.configopts = self.config[conf_section]
        else:
            self.config[conf_section] = {}
            self.configopts = self.config[conf_section]

        match self.configopts.get('Type', 'unused'):
          case "momentary":
            self.type = KeyTypes.MOMENTARY
          case "toggle":
            self.type = KeyTypes.TOGGLE
          case "toggle2":
            self.type = KeyTypes.TOGGLE2
          case _:
            self.type = KeyTypes.UNUSED
        
        self.inactive_label = self.configopts.get('InactiveLabel', '{}.OFF'.format(self.id))
        self.active_label = self.configopts.get('ActiveLabel', '{}.ON'.format(self.id))

        self.inactive_label_color = self.configopts.get('InactiveLabelColor', 'white')
        self.active_label_color = self.configopts.get('ActiveLabelColor', 'black')
        
        self.inactive_background = self.configopts.get('InactiveBackground', 'black')
        self.active_background = self.configopts.get('ActiveBackground', 'white')
        
        self.state = False

        self.hal.newpin(self.pin_name(self.deck, self.id, 'out'), hal.HAL_BIT, hal.HAL_OUT)
        self.hal.newpin(self.pin_name(self.deck, self.id, 'in'), hal.HAL_BIT, hal.HAL_IN)

        self.hasEnable = self.configopts.getboolean('EnablePin', False)
        if self.hasEnable:
            self.hal.newpin(self.pin_name(self.deck, self.id, 'enable'), hal.HAL_BIT, hal.HAL_IN)
            
        self.enabled = True


        self.update_key_image()
        
    def state(self):
        return self.state

    def state_poll(self):
        in_state = self.hal[self.pin_name(self.deck, self.id, 'in')]
        if self.hasEnable:
            enable_state = self.hal[self.pin_name(self.deck, self.id, 'enable')]
        else:
            enable_state = True

        if self.enabled != enable_state or self.state != in_state:
            self.state = in_state
            self.enabled = enable_state
            self.update_key_image()

    def pin_name(self, deck, key, name):
        #    return deck.get_serial_number() + "." + name + "." + str(key);
        return '{:01}.{:02}.{}'.format(0, key, name)
    
    def key_change(self, key_state):
        if self.enabled:
            self.hal[self.pin_name(deck, self.id, 'out')] = key_state
        
    def render_key_image(self):
        with self.deck:
            label = self.active_label if self.state else self.inactive_label
            color = self.active_label_color if self.state else self.inactive_label_color
            background = 'black' if not self.type != KeyTypes.UNUSED else self.active_background if self.state else self.inactive_background
            
            image = PILHelper.create_key_image(self.deck, background=background)
            
            if self.type != KeyTypes.UNUSED:
                draw = ImageDraw.Draw(image)
                fontsize = self.configopts.getint('fontsize', 14)
                font = ImageFont.truetype(os.path.join(ASSETS_PATH, "Roboto-Regular.ttf"), fontsize)
                draw.multiline_text((image.width / 2, image.height / 2), text=label, font=font, anchor="mm", align="center", fill=color)

            if not self.enabled:
                cover_image = Image.new('RGB', image.size, '#000000')
                image = Image.blend(image, cover_image, 0.7)
                image = image.filter(ImageFilter.GaussianBlur(radius=1.25))
                
            return PILHelper.to_native_key_format(self.deck, image)

    def update_key_image(self):
        image = self.render_key_image()

        with self.deck:
            self.deck.set_key_image(self.id, image)


keys = []

def key_change_callback(deck, key, state):
    print("Deck {} Key {} = {}".format(deck.id(), key, state), flush=True)

    with deck:
        keys[key].key_change(state)

if __name__ == "__main__":
    ap = argparse.ArgumentParser(prog='deckard.py', description='LinuxCNC StreamDeck support')
    ap.add_argument('configfile')

    args = ap.parse_args()
    print("config file={}".format(args.configfile))

    config = configparser.ConfigParser()
    config.read(args.configfile)
    
    decks = DeviceManager().enumerate()

    print("Deckard found {} deck(s).\n".format(len(decks)))

    for index, deck in enumerate(decks):
        if not deck.is_visual():
            continue

        deck.open()
        deck.reset()

        print("Opened '{}' device (serial number: '{}', fw: '{}')".format(
            deck.deck_type(), deck.get_serial_number(), deck.get_firmware_version()
        ))

        deck.set_brightness(100)
       
        for key in range(deck.key_count()):
            keys.append(Key(deckref=deck, halref=HAL, confref=config, id=key))
            
                    
        def update():
            while deck.is_open():
                try:
                    for key in range(deck.key_count()):
                        keys[key].state_poll()
                                
                except TransportError:
                    
                    break
                
        threading.Thread(target=update).start()
            
        # Register callback function for when a key state changes.
        deck.set_key_callback(key_change_callback)

        HAL.ready()

        for t in threading.enumerate():
            try:
                t.join()
            except RuntimeError:
                pass
            except KeyboardInterrupt:
                with deck:
                    deck.reset()
                    deck.close()
                
