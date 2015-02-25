"""
The MovingSign class handles parsing of "Moving Sign"
Communication Protocol V1.2. This class allows you to 
construct an ASCII encoded command to program text, 
graphics, and special functions for a 'BigBrite' LED sign.

Protocol format consists of a 5 byte start command, 5 byte 
header, Data field of max 4K message length, 6 byte message end
including a 4 byte checksum.

# Communication protocol payload format
  
# Command Code (1 byte)
# 'A' - Write text file command
# 'C' - Write variable command
# 'E' - Write graphics file command
# 'W' - Write special function command
# 'R' - Read special function (Not used)
  
# File name (1 byte)
# '0-9','A-Z' - Filename LED storage, sign cycles through sequentially
  
# Pause Time (1 byte)
# '0-9' - 0 to 9 seconds

# Show date (2 bytes)
# If date is allowed to display, then bit is 1, otherwise 0.
# Example: Sunday, Monday, Thursday is '13'. All week is '7F'
  
# bit0 - Sunday
# bit1 - Monday
# bit2 - Tuesday
# bit3 - Wednesday
# bit4 - Thursday
# bit5 - Friday
# bit6 - Saturday
# bit7 - null
    
# Start Show Time (4 bytes)
# Two ASCII characters for hour, two for minute. 
# Example: 3:23am is '0323'
# '00-24' - hour
# '00-59' - minute 
 
# End Show Time (4 bytes)
# Two ASCII characters for hour, two for minute. 
# Example: 3:23pm is '1523'
# '00-24' - hour
# '00-59' - minute
  
# Preparative (3 bytes)
# For future applications... or never. Always 0
# Example: '000'
# '0-0' - O_O
  
# Graphics File (2 bytes)
# Lead Character 0xFC
# '0-9','A-Z' - Graphics filename

# Variable (2 bytes)
# Lead Character 0xFB
 
# 'A' - hh:mm:ss
# 'B' - hh:mm:ss AM/PM
# 'C' - hh:mm
# 'D' - hh:mm AM/PM
# 'E' - mm/dd/yyyy
# 'F' - yyyy-mm-dd
# 'G' - dd.MM yyyy
# 'H' - mm'dd'yyyy
# 'I' - English week shortened form 
# 'J' - English week full form
# 'K' - Count down (hh:mm:ss), after the K, 6 bytes show the start time
#       another 6 bytes show the end time.
#       Example: '010030000130' shows the start countdown time is
#       01:00:30, countdown time is 1 minute 30 second
# 'L' - Count down (date) after the 'L' 6 bytes show the end date
#       Example: '051023' shows the end date is 2005-10-23
        
# Temperature (2 bytes)
# Lead character 0xF9
# 'A' - Fahrenheit
# 'B' - Celsius
  
# Enter (1 byte)
# 0x7F
  
# ASCII (1 byte)
# 0x20 - 0x7E valid characters

"""  

from time import strftime

class MovingSign(object):
    """
    MovingSign class
    """
    NUL = '\x00'
    SOH = '\x01'
    STX = '\x02'
    ETX = '\x03'
    EOT = '\x04'
    FONT_VAL = '\xFE'
    COLOR_VAL = '\xFD'

    CMD_WRITE_TXT = b'A'
    CMD_WRITE_VAR = b'C'
    CMD_WRITE_GFX = b'E'
    CMD_WRITE_SPC = b'W'
    CMD_READ_SPC = b'R'

    DISPLAY_MODE = {
        "auto": 'A',
        "flash": 'B',
        "hold": 'C',
        "interlock": 'D',
        "rolldown": 'E',
        "rollup": 'F',
        "rollin": 'G',
        "rollleft": 'I',
        "rollright": 'J',
        "rotate": 'K',
        "slide": 'L',
        "snow": 'M',
        "sparkle": 'N',
        "spray": 'O',
        "starburst": 'P',
        "switch": 'Q',
        "twinkle": 'R',
        "wipedown": 'S',
        "wipeup": 'T',
        "wipein": 'U',
        "wipeout": 'V',
        "wipeleft": 'W',
        "wiperight": 'X',
        "cyclecolor": 'Y',
        "clock": 'Z'
    }

    DISPLAY_SPEED = {
        "faster": '0',
        "fast": '1',
        "normal": '2',
        "slow": '3',
        "slower": '4'
    }

    ALIGN = {
        "left": '1',
        "right": '2',
        "center": '3'
    }

    FONT = { # Lead character 0xFE
        "SS5": 'A', # Short Narrow
        "ST5": 'B', # Short Normal
        "WD5": 'C', # Short Wide
        "WS5": 'D', # Short Wider
        "SS7": 'E', # Tall Narrow
        "ST7": 'F', # Tall Normal
        "WD7": 'G', # Tall Wide
        "WS7": 'H', # Tall Wider
        "SDS": 'I', # Drop Shadow
        "SRF": 'J', # Narrow Serif
        "STF": 'K', # Normal Serif
        "WDF": 'L', # Wide Serif
        "WSF": 'M', # Wider Serif
        "SDF": 'N', # Drop Shadow Serif
        "SS10": 'O', # wider?
        "ST10": 'P', # wider?
        "WD10": 'Q', # wider?
        "WS10": 'R', # wider?
        "SS15": 'S', # Narror Narrow Lead
        "ST15": 'T', # Normal Narrow Lead
        "WD15": 'U', # Wide Narrow Lead
        "WS15": 'V', # Wider Narrow Lead
        "SS23": 'W', # too big, condensed to narrow
        "SS31": 'X', # too big, condensed to narrow
        "SMALL": '@' # Very Narrow
    }

    COLOR = { # Lead character 0xFD
        "auto": 'A',
        "lightred": 'B',
        "lightgreen": 'C',
        "red": 'D',
        "green": 'E',
        "yellow": 'F',
        "brown": 'G',
        "amber": 'H',
        "orange": 'I',
        "mix1": 'J', # Reggae (Red / Green / Yellow)
        "mix2": 'K', # Interleaved RGY
        "mixh": 'L', # Vertical Lines
        "black": 'M'
    }

    SYMBOLS = {
        "sunburst": '\xd0',
        "clock": '\xd1',
        "telephone": '\xd2',
        "sunglasses": '\xd3',
        "faucet": '\xd4',
        "bug": '\xd5',
        "key": '\xd6',
        "shirt": '\xd7',
        "helicopter": '\xd8',
        "car": '\xd9',
        "lantern": '\xda',
        "pyramid": '\xdb', # pyramid with legs?
        "whale": '\xdc',
        "scooter": '\xdd',
        "bicycle": '\xde',
        "crown": '\xdf',
        "dheart": '\xe0', # double heart?
        "rarrow": '\xe1', # right arrow
        "larrow": '\xe2', # left arrow
        "ldarrow": '\xe3', # left down arrow
        "luarrow": '\xe4', # left up arrow
        "gas": '\xe5', # sideways gas?
        "chair": '\xe6',
        "shoe": '\xe7', # high heeled shoe
        "martini": '\xe8', 
        "envelope": '\xe9',
        "hamburger": '\xea' # top of a hamburger w/ eyes
    }

    def __init__(self, sdr_addr = b"FF", rcv_addr = b"00"):
        """
        Initiates MovingSign message instance.
        """
        self.sdr_addr = sdr_addr
        self.rcv_addr = rcv_addr
        self.filename = b'A'
        self.display_mode = b'A'
        self.display_speed = b'2'
        self.pause_time = b'2'
        self.show_date = b"7F"
        self.start_time = b"0000"
        self.stop_time = b"2400"
        self.prep = b"000"
        self.align = b'3'
        self.header = bytearray([self.NUL, self.NUL, self.NUL, self.NUL, self.NUL])

    def checksum(self, mesg):    
        """
        Generate checksum of 4 bytes
        generated from sum of bytes from 
        data message payload.
        """
        val = sum(bytearray(mesg))
        return b'{:04X}'.format(val)

    def set_sdr_addr(self, sender):
        """
        Set sender address
        """
        self.sdr_addr = sender

    def set_rcv_addr(self, receiver):
        """
        Set receiver address
        """
        self.rcv_addr = receiver

    def set_display_mode(self, display_mode):
        """
        Set display mode
        """
        self.display_mode = display_mode

    def set_display_speed(self, display_speed):
        """
        Set display speed
        """
        self.display_speed = display_speed

    def set_display_align(self, align):
        """
        Set display speed
        """
        self.align = align

    def protocol(self, mesg):
        """
        Create finalized protocol string
        including header details, message, 
        and checksum values.
        """
        cmd = bytearray([])
        cmd += self.header
        cmd += self.SOH
        cmd += self.sdr_addr
        cmd += self.rcv_addr
        cmd += mesg
        cmd += self.checksum(mesg)
        cmd += self.EOT
        return cmd

    def cmd_txt(self, data):
        """
        Write text command
        """
        mesg = bytearray([self.STX])
        mesg += self.CMD_WRITE_TXT
        mesg += self.filename
        mesg += self.display_mode
        mesg += self.display_speed
        mesg += self.pause_time
        mesg += self.show_date
        mesg += self.start_time
        mesg += self.stop_time
        mesg += self.prep
        mesg += self.align
        mesg += data
        mesg += self.ETX
        return self.protocol(mesg)

    def cmd_var(self, var, attr, data):
        """
        Write variable command
        """
        mesg = bytearray([self.STX])
        mesg += self.CMD_WRITE_VAR
        mesg += var
        mesg += attr
        mesg += data
        mesg += self.ETX
        return self.protocol(mesg)

    def cmd_gfx(self, attr, data):
        """
        Write graphics command for
        sending special operations.
        Command Attribute (5 bytes):
        Height and Width
        XX,XX
        Graphics Data, one line at a time
        'B' - Light Red
        'C' - Light Green
        'D' - Red
        'E' - Green
        'F' - Yellow
        'G' - Brown
        'H' - Amber
        'I' - Orange
        'M' - Black
        """
        mesg = bytearray([self.STX])
        mesg += self.CMD_WRITE_GFX
        mesg += self.filename
        mesg += attr
        mesg += data
        mesg += self.ETX
        return self.protocol(mesg)

    def cmd_write_special(self, data):
        """
        Write control command for
        sending special operations.
        """
        mesg = bytearray([self.STX])
        mesg += self.CMD_WRITE_SPC
        mesg += data
        mesg += self.ETX
        return self.protocol(mesg)

    def cmd_read_special(self, data):
        """
        Read control command for
        retrieving special operations.
        """
        mesg = bytearray([self.STX])
        mesg += self.CMD_READ_SPC
        mesg += data
        mesg += self.ETX
        return self.protocol(mesg)

    def clear(self):
        """
        Clear all files in memory
        Subcontrol command: 'L'
        """
        mesg = self.cmd_write_special('L')
        return mesg

    def reset(self):
        """
        Send reset signal to LED sign
        Subcontrol command: 'B'
        """
        mesg = self.cmd_write_special('B')
        return mesg

    def clock(self, datetimeweek):
        """
        Clock with 15 char decimal format
        Subcontrol command: 'A'
        Command Data:
        YYYYMMDDHHMMSSW
        Year/Month/Day/Hour/Minute/Second/Weekday
        """
        mesg = self.cmd_write_special(b'A' + datetimeweek)
        return mesg

    def clock_sync(self):
        """
        Clock with time sync to local host
        """
        mesg = self.clock(strftime("%Y%m%d%H%M%S%w"))
        return mesg
        
    def passwd(self, passwd):
        """
        Set password (6 ASCII char)
        Subcontrol command: 'C'
        Command Data:
        XXXXXX
        """
        mesg = self.cmd_write_special(b'C' + passwd)
        return mesg

    def set_dev_num(self, num):
        """
        Set device number (2 byte 0x01-0xFE)
        Subcontrol command: 'D'
        Command Data:
        XX
        """
        mesg = self.cmd_write_special(b'D' + num)
        return mesg

    def set_display_times(self, display_times):
        """
        Set display times (40 bytes)
        Subcontrol command: 'E'
        Command Data:
        Four start / end time pairings of format
        SHSM,EHEM;
        SHSM,EHEM;
        SHSM,EHEM;
        SHSM,EHEM.
        """
        mesg = self.cmd_write_special(b'E' + display_times)
        return mesg

    def set_display_file_mode(self, display_file_mode):
        """
        Set display mode (1 bytes)
        Subcontrol command: 'F'
        Command Data:
        'A' - Display all files
        'T' - Display files according to time
        """
        mesg = self.cmd_write_special(b'F' + display_mode)
        return mesg

    def set_cue_voice(self, cue):
        """
        Set cue voice (1 bytes)
        Subcontrol command: 'J'
        Command Data:
        '1' - Turn on
        '0' - Turn off
        """
        mesg = self.cmd_write_special(b'J' + cue)
        return mesg

    def set_passwd_mode(self, mode):
        """
        Set password mode (1 bytes)
        Subcontrol command: 'K'
        Command Data:
        '1' - Turn on
        '0' - Turn off
        """
        mesg = self.cmd_write_special(b'K' + mode)
        return mesg

    def set_brightness(self, level):
        """
        Set brightness level (1 bytes)
        Subcontrol command: 'P'
        Command Data:
        'A' - Autobrightness
        'T' - Control brightness to setup
        '1-8' - Brightness level
        """
        mesg = self.cmd_write_special(b'P' + level)
        return mesg

