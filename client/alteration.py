# -*- coding: utf-8-*-
import re


def detectYears(input):
    YEAR_REGEX = re.compile(r'(\b)(\d\d)([1-9]\d)(\b)')
    return YEAR_REGEX.sub('\g<1>\g<2> \g<3>\g<4>', input)

def simplifyURLs(input):
    # Only affects URLs that start with http(s)://
    # Removes http(s)://
    # Removes "www.", but not other subdomains
    # Removes paths unless they are short enough for a human to remember (i.e. have no slashes)
    # Removes trailing "/"
    # Retains ending sentence punctuation (.?!), but doesn't get confused if those chars are inside the URL
    # http://www.example.com/shorter -> example.com/shorter
    URL_REGEX_SHORT = re.compile(r'\bhttps?://(www\.|(\w+\.))?([A-Za-z0-9\.\-]+/[\w\.]*[^\W\.])/?(!|\.|\?|)(\s|$)')
    # http://www.example.com/long/annoying/ -> example.com
    URL_REGEX = re.compile(r'\bhttps?://(www\.|(\w+\.))?([A-Za-z0-9\.\-]+)(/(\S*([^\.!\?\$\s])|))?(\.|\?|!|)(\s|$|)')
    return URL_REGEX.sub(lambda m: (m.group(2)or'')+m.group(3)+m.group(7)+m.group(8), \
                         URL_REGEX_SHORT.sub(lambda m: (m.group(2)or'')+m.group(3)+m.group(4)+m.group(5), input))

def detectLVL1(input):
    LVL1_REGEX = re.compile(r'(?i)\blvl1\b')
    return LVL1_REGEX.sub('level-1', input)

def detectAmpersand(input):
    AMPERSAND_REGEX = re.compile(r'&')
    return AMPERSAND_REGEX.sub('and', input)

def clean(input):
    """
        Manually adjust output text before it's translated into
        actual speech by the TTS system. This is to fix minior
        idiomatic issues, for example, that 1901 is pronounced
        "one thousand, ninehundred and one" rather than
        "nineteen oh one".

        Arguments:
        input -- original speech text to-be modified
    """
    return detectAmpersand(detectLVL1(detectYears(simplifyURLs(input))))
