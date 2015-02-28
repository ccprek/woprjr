# -*- coding: utf-8-*-
from sys import maxint
import random
import re
import jasperpath
import os
import alsaaudio

WORDS = ["MUTE", "UNMUTE"]

PRIORITY = 4

def handle(text, mic, profile):
    """
        Responds to user-input, typically speech text, and mutes or unmutes responses

        Arguments:
        text -- user-input, typically transcribed speech
        mic -- used to interact with the user (for both input and output)
        profile -- contains information related to the user (e.g., phone
                   number)
    """

    mixer = alsaaudio.Mixer(control='PCM', cardindex=1)

    print mixer.getmute()[0]

    if (mixer.getmute()[0] == 1):
        # Unmute
        mixer.setmute(0)
        mic.say("Unmuting.")
    else:
        # Mute
        mic.say("Muting.")
        mixer.setmute(1)

def isValid(text):
    """
    Returns True if the input is related to mute

    Arguments:
    text -- user-input, typically transcribed speech
    """
    return bool(re.search(r'\bmute\b', text, re.IGNORECASE))
