# -*- coding: utf-8-*-
from sys import maxint
import random
import jasperpath
import os

WORDS = []

PRIORITY = -(maxint + 1)

def handle(text, mic, profile):
    """
        Reports that the user has unclear or unusable input.

        Arguments:
        text -- user-input, typically transcribed speech
        mic -- used to interact with the user (for both input and output)
        profile -- contains information related to the user (e.g., phone
                   number)
    """

    # Respond with random soundboard file
    responses = os.listdir(jasperpath.data('audio', 'soundboards'))
    response = random.choice(responses)

    mic.speaker.play(jasperpath.data('audio', 'soundboards', response))


def isValid(text):
    return True
