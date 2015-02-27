# -*- coding: utf-8-*-
import urllib2
from client import app_utils
import re
from bs4 import BeautifulSoup
from bs4.element import Comment

WORDS = ["YES", "SURE", "YEAH", "NO", "DON'T", "STOP", \
         "FIRST_TIME", "VISITOR", "INFO", \
         "EQUIPMENT", "AND", "SUPPLIES", "WANTED", "NEEDED", \
         "SPACE", "UPGRADE", "UPGRADES", \
         "DOWNGRADE", "DOWNGRADES", \
         "REGULAR", "MEETUP", "MEETUPS", \
         "UPCOMING", "WORKSHOP", "WORKSHOPS", "EVENT", "EVENTS", \
         "PROJECT", "ROLL", "CALL", \
         "MEETING", "NOTES"]

PRIORITY = 4

URL = 'http://wiki.lvl1.org'
MINUTES_HEADING_ID = 'Recent_Meetings'

class Section:
    def __init__(self, elem_list):
        self.elem_list = elem_list

    def title(self):
        return self.elem_list[0].get_text().strip()

    def __repr__(self):
        return "<Section title=%r >" % self.title()

    def to_speakable_string(self):
        def stringify(elem):
            if type(elem) is Comment:
                # Ignore HTML comments
                return ''
            if "get_text" in dir(elem):
                return elem.get_text().strip()
            else:
                return elem.strip()
        def simplify_whitespace(text):
            WHITESPACE_REGEX = re.compile(r'([.!?])?(\s*\n\s*)')
            return WHITESPACE_REGEX.sub(lambda m: (m.group(1) or ".")+" ", text)
        return simplify_whitespace("\n".join(map(stringify, self.elem_list)))
        

def getRecentMinutesURL():
    hdr = {'User-Agent': 'Mozilla/5.0'}
    req = urllib2.Request(URL, headers=hdr)
    page = urllib2.urlopen(req).read()
    soup = BeautifulSoup(page)
    heading = soup.find('span', id=MINUTES_HEADING_ID)
    # The next list element is the most recent minutes listing
    li = heading.find_next('li')
    a = li.findChild('a')
    # Might not work if URL ends with '/'
    return URL + a.attrs['href']

def getMinutesSections(date=None):
    """
        Returns the given minutes in a structured way.

        Arguments:
        date -- the date of the minutes to look at as a string "mm/dd/yyyy".
                Defaults to most recent.
    """
    if (date==None):
        minURL = getRecentMinutesURL()
    else:
        # Might not work if URL ends with '/'
        minURL = URL + "/" + date
    hdr = {'User-Agent': 'Mozilla/5.0'}
    req = urllib2.Request(minURL, headers=hdr)
    page = urllib2.urlopen(req).read()
    soup = BeautifulSoup(page)
    headings = soup.findAll('span', class_="mw-headline")
                
    def headingToSection(heading_title):
        # heading_title is really a span within a h1, h2..hn tag
        heading = heading_title.parent
        gen = heading.next_siblings
        elem_list = [heading]
        try:
            elem = gen.next()
            while elem.name != heading.name:
                elem_list.append(elem)
                elem = gen.next()
        except StopIteration:
            pass
        return Section(elem_list)
        
    section_list = [headingToSection(h) for h in headings]
    section_dict = {}
    for sec in section_list:
        section_dict[sec.title().lower()] = sec
    return section_dict


def handle(text, mic, profile):
    """
        Responds to user-input, typically speech text, with a sample of
        Hacker News's top headlines, sending them to the user over email
        if desired.

        Arguments:
        text -- user-input, typically transcribed speech
        mic -- used to interact with the user (for both input and output)
        profile -- contains information related to the user (e.g., phone
                   number)
    """
    section_title = getMatchingSectionTitle(text)
    def handleResponse(text):
        if app_utils.isPositive(text):
            mic.say("Checking the minutes...")
            sections = getMinutesSections()
            section = sections[section_title.lower()]
            mic.say(section.to_speakable_string())
        else:
            mic.say("Nevermind.")
    mic.say("Would you like to hear %s?" % section_title)
    handleResponse(mic.activeListen())

def isValid(text):
    """
        Returns True if the input is related to Hacker News.

        Arguments:
        text -- user-input, typically transcribed speech
    """
    return getMatchingSectionTitle(text) is not None

def getMatchingSectionTitle(text):
    "Returns None if not found, otherwise the title of the section"
    if bool(re.search(r'\bfirst[ _]time (visitor )?(info)?\b', text, re.IGNORECASE)):
        return "First time visitor info"
    elif bool(re.search(r'\b(equipment (and )?supplies|supplies (and )?equipment|equipment|supplies)( wanted| needed)?\b', text, re.IGNORECASE)):
        return "Equipment and supplies wanted"
    elif bool(re.search(r'\b(space )?upgrades?\b', text, re.IGNORECASE)):
        return "Space upgrades"
    elif bool(re.search(r'\b(space )?downgrades?\b', text, re.IGNORECASE)):
        return "Space downgrades"
    elif bool(re.search(r'\b(regular )?meetups?\b', text, re.IGNORECASE)):
        return "Regular meetups"
    elif bool(re.search(r'\b(upcoming )?(workshops? (and )?events?|events? (and )?workshops?|workshops?|events?)\b', text, re.IGNORECASE)):
        return "Upcoming workshops and events"
    elif bool(re.search(r'\b(projects?|(projects? )?roll call)\b', text, re.IGNORECASE)):
        return "Project roll call"
    elif bool(re.search(r'\bmeeting notes?\b', text, re.IGNORECASE)):
        return "Meeting notes"
    else:
        return None
