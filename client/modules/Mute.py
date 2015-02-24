# -*- coding: utf-8-*-
from sys import maxint
import random
import jasperpath
import os
import alsaaudio

WORDS = []

PRIORITY = -(maxint + 1)

def handle(text, mic, profile):
    """
        Responds to user-input, typically speech text, and mutes or unmutes responses

        Arguments:
        text -- user-input, typically transcribed speech
        mic -- used to interact with the user (for both input and output)
        profile -- contains information related to the user (e.g., phone
                   number)
    """

    mixer = alsaaudio.Mixer()

    if (mixer.getmute):
        # Unmute
        mixer.setmute(0)
        mic.say("Unmuting")
    else:
        # Mute
        mic.say("Muting")
        mixer.setmute(1)

def isValid(text):
    return True
