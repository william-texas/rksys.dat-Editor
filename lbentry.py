from pkg_resources import parse_version
from kaitaistruct import KaitaiStruct, KaitaiStream, BytesIO
from mii import Mii
from bitstring import BitStream, BitArray
import binascii


def hex_string(data):
    return str(binascii.hexlify(data).upper())[2:-1]


def clean_mii_name(name):
    name, sep, garbgae = name.partition('\x00')
    if name.lstrip() == '':
        return 'No Record'
    elif name.lstrip() == '\x18':
        return 'Best Split'
    else:
        return name.lstrip()


class MkwLbEntry(KaitaiStruct):
    def __init__(self, _io, _parent=None, _root=None):
        self._io = _io
        self._parent = _parent
        self._root = _root if _root else self
        self._read()

    def _read(self):
        self.mii = self._io.read_bytes(74)
        self.crc16 = self._io.read_bytes(2)
        self.mins = self._io.read_bits_int_be(7)
        # print(bin(self.mins))
        self.seconds = self._io.read_bits_int_be(7)
        # print(bin(self.seconds))
        self.milliseconds = self._io.read_bits_int_be(10)
        # print(bin(self.milliseconds))
        self.vehicle = self._io.read_bits_int_be(6)
        self.enabled = self._io.read_bits_int_be(3)
        self.characterid = self._io.read_bits_int_be(7)
        self.controllerid = self._io.read_bits_int_be(3)
        self.unknown1 = self._io.read_bits_int_be(5)
        self._io.align_to_byte()
        self.unknown2 = self._io.read_bytes(14)


class MkwSplitEntry(KaitaiStruct):
    def __init__(self, _io, _parent=None, _root=None):
        self._io = _io
        self._parent = _parent
        self._root = _root if _root else self
        self._read()

    def _read(self):
        self.mins = self._io.read_bits_int_be(7)
        self.seconds = self._io.read_bits_int_be(7)
        self.milliseconds = self._io.read_bits_int_be(10)


character_dict = {0:"Mario", 1:"Baby Peach", 2:"Waluigi", 3:"Bowser", 4:"Baby Daisy", 5:"Dry Bones", 6:"Baby Mario", 7:"Luigi", 8:"Toad", 9:"Donkey Kong", 10:"Yoshi", 11:"Wario", 12:"Baby Luigi", 13:"Toadette", 14:"Koopa", 15:"Daisy", 16:"Peach", 17:"Birdo", 18:"Diddy Kong", 19:"King Boo", 20:"Bowser Jr.", 21:"Dry Bowser", 22:"Funky Kong", 23:"Rosalina", 24:"Small Mii A Male", 25:"Small Mii A Female", 26:"Small Mii B Male", 27:"Small Mii B Female", 30:"Medium Mii A Male", 31:"Medium Mii A Female", 32:"Medium Mii B Male", 33:"Medium Mii B Female", 36:"Large Mii A Male", 37:"Large Mii A Female", 38:"Large Mii B Male", 39:"Large Mii B Female"}
vehicle_dict = {0:"Standard Kart S", 1:"Standard Kart M", 2:"Standard Kart L", 3:"Booster Seat", 4:"Classic Dragster", 5:"Offroader", 6:"Mini Beast", 7:"Wild Wing", 8:"Flame Flyer", 9:"Cheep Charger", 10:"Super Blooper", 11:"Piranha Prowler", 12:"Tiny Titan", 13:"Daytripper", 14:"Jetsetter", 15:"Blue Falcon", 16:"Sprinter", 17:"Honeycoupe", 18:"Standard Bike S", 19:"Standard Bike M", 20:"Standard Bike L", 21:"Bullet Bike", 22:"Mach Bike", 23:"Flame Runner", 24:"Bit Bike", 25:"Sugarscoot", 26:"Wario Bike", 27:"Quacker", 28:"Zip Zip", 29:"Shooting Star", 30:"Magikruiser", 31:"Sneakster", 32:"Spear",  33:"Jet Bubble", 34:"Dolphin Dasher", 35:"Phantom"}
controller_dict = {0:'Wii Wheel', 1:'Nunchuck', 2:'Classic Controller', 3:'GCN Controller'}


# create_split_hex(2, 22, 122)

def view_top5(course, license):
    license = 0x08 + (license - 1) * 0x8cc0
    with open('rksys.dat', 'rb') as f:
        for i in range(5):
            f.seek(license + 0xdc0 + 0x60 * course + i * 0xc00)
            lbentry = MkwLbEntry.from_bytes(f.read(96))
            mii = Mii.from_bytes(lbentry.mii)
            print()
            if lbentry.enabled != 0:
                print(f'{i+1}: {clean_mii_name(mii.mii_name)} - {lbentry.mins}:{str(lbentry.seconds).zfill(2)}.{str(lbentry.milliseconds).zfill(3)} - {character_dict.get(lbentry.characterid)} on {vehicle_dict.get(lbentry.vehicle)} with {controller_dict.get(lbentry.controllerid)}')
            else:
                print('No Record.')
        f.seek(license + 0xdc0 + 0x60 * course + 5 * 0xc00)
        lbentry = MkwLbEntry.from_bytes(f.read(96))
        if lbentry.enabled != 0:
            print(f'\nBest Split: {lbentry.mins}:{str(lbentry.seconds).zfill(2)}.{str(lbentry.milliseconds).zfill(3)} - {character_dict.get(lbentry.characterid)} on {vehicle_dict.get(lbentry.vehicle)} with {controller_dict.get(lbentry.controllerid)}')
        else:
            print('\nNo Best Split.')
        f.close()

# track_dict = {0: 'Luigi Circuit', 1: 'Moo Moo Meadows',
#               2: 'Mushroom Gorge', 3: "Toad's Factory", 4: 'Mario Circuit',
#               5: 'Coconut Mall', 6: 'DK Summit', 7: "Wario's Gold Mine",
#               8: 'Daisy Circuit', 9: 'Koopa Cape', 11: 'Maple Treeway',
#               10: 'Grumble Volcano', 13: 'Dry Dry Ruins', 12: 'Moonview Highway',
#               14: "Bowser's Castle", 15: 'Rainbow Road', 24: 'GCN Peach Beach',
#               28: 'DS Yoshi Falls', 17: 'SNES Ghost Valley 2', 21: 'N64 Mario Raceway',
#               20: 'N64 Sherbet Land', 16: 'GBA Shy Guy Beach', 31: 'DS Delfino Square',
#               26: 'GCN Waluigi Stadium', 29: 'DS Desert Hills', 19: 'GBA Bowser Castle 3',
#               22: "N64 DK's Jungle Parkway", 25: 'GCN Mario Circuit', 18: 'SNES Mario Circuit 3',
#               30: 'DS Peach Gardens', 27: 'GCN DK Mountain', 23: "N64 Bowser's Castle"}

track_dict = {"LUIGI CIRCUIT": 0, "LC": 0, "MOO MOO MEADOWS": 1, "MMM": 1, "MUSHROOM GORGE": 2, "MG": 2,
              "TOAD'S FACTORY": 3, "TF": 3, "MARIO CIRCUIT": 4, "MC": 4, "COCONUT MALL": 5, "CM": 5, "DK SUMMIT": 6,
              "DKS": 6, "DKSC": 6, "WARIO'S GOLD MINE": 7, "WGM": 7, "DAISY CIRCUIT": 8, "DC": 8, "KOOPA CAPE": 9,
              "KC": 9, "MAPLE TREEWAY": 11, "MT": 11, "GRUMBLE VOLCANO": 10, "GV": 10, "DRY DRY RUINS": 13, "DDR": 13,
              "MOONVIEW HIGHWAY": 12, "MH": 12, "BOWSER'S CASTLE": 14, "BC": 14, "BCWII":14, "RAINBOW ROAD": 15, "RR": 15,
              "GCN PEACH BEACH": 24, "RPB": 24, "DS YOSHI FALLS": 28, "RYF": 28, "SNES GHOST VALLEY 2": 17, "RGV2": 17,
              "N64 MARIO RACEWAY": 21, "RMR": 21, "N64 SHERBET LAND": 20, "RSL": 20, "GBA SHY GUY BEACH": 16,
              "RSGB": 16, "DS DELFINO SQUARE": 31, "RDS": 31, "GCN WALUIGI STADIUM": 26, "RWS": 26,
              "DS DESERT HILLS": 29, "RDH": 29, "GBA BOWSER CASTLE 3": 19, "RBC3": 19, "N64 DK'S JUNGLE PARKWAY": 22,
              "RDKJP": 22, "GCN MARIO CIRCUIT": 25, "RMC": 25, "SNES MARIO CIRCUIT 3": 18, "RMC3": 18,
              "DS PEACH GARDENS": 30, "RPG": 30, "GCN DK MOUNTAIN": 27, "RDKM": 27, "N64 BOWSER'S CASTLE": 23,
              "RBC": 23}


# view_top5(14, 3)
def main_logic():
    more_changes = True
    while more_changes:
        decision = input('Type "view" to view a Top 5 or type "edit" to edit a Top 5: ')
        if decision.upper() == 'VIEW':
            track = input('Enter a track to view: ').upper()
            license = input("Enter which license to use (1-4): ")
            view_top5(int(track_dict[track]), int(license))
        elif decision.upper() == 'EDIT':
            track = input('Which track do you want to edit? ').upper()
            license = input("Enter which license to use (1-4): ")
            view_top5(int(track_dict[track]), int(license))
            time_to_edit = input('Which position do you want to edit (1-5, type 6 for best split)? ')
            if int(time_to_edit) not in [1, 2, 3, 4, 5, 6]:
                raise Exception()
            else:
                time_to_edit = int(time_to_edit)
            f = open('rksys.dat', 'rb+')
            license = 0x08 + (int(license) - 1) * 0x8cc0
            f.seek(license + 0xdc0 + 0x60 * int(track_dict[track]) + (time_to_edit - 1) * 0xc00)
            print(f.tell())
            edit_loc = f.tell()
            lbentry = MkwLbEntry.from_bytes(f.read(96))
            print(str(lbentry.mins) + ':' + str(lbentry.seconds).zfill(2) + '.' + str(lbentry.milliseconds).zfill(3))
            print('This is what this entry currently is. Please enter the time you want to change it to. '
                  '\n(I am not responsible if entering mistyped time values corrupts your save!)')
            character_ids = {v: k for k, v in character_dict.items()}
            vehicle_ids = {v: k for k, v in vehicle_dict.items()}
            minutes = int(input('Minutes: '))
            seconds = int(input('Seconds: '))
            milliseconds = int(input('Milliseconds: '))
            minutes = format(minutes, '07b')
            seconds = format(seconds, '07b')
            milliseconds = format(milliseconds, '010b')
            character = character_ids.get(input('Character: '))
            vehicle = vehicle_ids.get(input('Vehicle (American names used): '))
            byte = minutes + seconds + milliseconds + format(vehicle, '06b') + format(1, '03b') + format(character, '07b')
            byte = BitArray(bin=byte)
            f.seek(edit_loc + 76)
            f.write(binascii.unhexlify(byte.hex))
            f.seek(0)
            crc32 = binascii.crc32(f.read(0x27ffc))
            f.seek(0x27ffc)
            f.write(crc32.to_bytes(4, 'big'))
            print('Changes saved.')

        more_changes = input('\nMake more changes (y/n)? ')
        more_changes = False if more_changes.upper() == 'N' else True



if __name__ == '__main__':
    main_logic()
#lol