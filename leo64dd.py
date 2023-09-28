#
#   64DD Python module
#
#   Based on https://github.com/jkbenaim/leotools/blob/master/leogeo.c
#   Originally sourced from https://github.com/Drahsid/mario-paint
#

import struct, sys, numpy

sys_lba_count = 24
lba_count = 4316
sector_count = 85

sys_lba_tbl_retail = (0, 1,  8,  9)
sys_lba_tbl_dev =    (2, 3, 10, 11)
sys_lba_tbl_diskid = (14, 15)
ram_lba_start_tbl = (0x5A2, 0x7C6, 0x9EA, 0xC0E, 0xE32, 0x1010, 0x10DC)

block_size_per_pzone = ( 19720, 18360, 17680, 16320, 14960, 13600, 12240, 10880, 9520 )

vzone_lba_tbl = (
    (0x0124, 0x0248, 0x035A, 0x047E, 0x05A2, 0x06B4, 0x07C6, 0x08D8, 0x09EA, 0x0AB6, 0x0B82, 0x0C94, 0x0DA6, 0x0EB8, 0x0FCA, 0x10DC),
    (0x0124, 0x0248, 0x035A, 0x046C, 0x057E, 0x06A2, 0x07C6, 0x08D8, 0x09EA, 0x0AFC, 0x0BC8, 0x0C94, 0x0DA6, 0x0EB8, 0x0FCA, 0x10DC),
    (0x0124, 0x0248, 0x035A, 0x046C, 0x057E, 0x0690, 0x07A2, 0x08C6, 0x09EA, 0x0AFC, 0x0C0E, 0x0CDA, 0x0DA6, 0x0EB8, 0x0FCA, 0x10DC),
    (0x0124, 0x0248, 0x035A, 0x046C, 0x057E, 0x0690, 0x07A2, 0x08B4, 0x09C6, 0x0AEA, 0x0C0E, 0x0D20, 0x0DEC, 0x0EB8, 0x0FCA, 0x10DC),
    (0x0124, 0x0248, 0x035A, 0x046C, 0x057E, 0x0690, 0x07A2, 0x08B4, 0x09C6, 0x0AD8, 0x0BEA, 0x0D0E, 0x0E32, 0x0EFE, 0x0FCA, 0x10DC),
    (0x0124, 0x0248, 0x035A, 0x046C, 0x057E, 0x0690, 0x07A2, 0x086E, 0x0980, 0x0A92, 0x0BA4, 0x0CB6, 0x0DC8, 0x0EEC, 0x1010, 0x10DC),
    (0x0124, 0x0248, 0x035A, 0x046C, 0x057E, 0x0690, 0x07A2, 0x086E, 0x093A, 0x0A4C, 0x0B5E, 0x0C70, 0x0D82, 0x0E94, 0x0FB8, 0x10DC),
)

pzone_tbl = (
    (0x0, 0x1, 0x2, 0x9, 0x8, 0x3, 0x4, 0x5, 0x6, 0x7, 0xF, 0xE, 0xD, 0xC, 0xB, 0xA),
    (0x0, 0x1, 0x2, 0x3, 0xA, 0x9, 0x8, 0x4, 0x5, 0x6, 0x7, 0xF, 0xE, 0xD, 0xC, 0xB),
    (0x0, 0x1, 0x2, 0x3, 0x4, 0xB, 0xA, 0x9, 0x8, 0x5, 0x6, 0x7, 0xF, 0xE, 0xD, 0xC),
    (0x0, 0x1, 0x2, 0x3, 0x4, 0x5, 0xC, 0xB, 0xA, 0x9, 0x8, 0x6, 0x7, 0xF, 0xE, 0xD),
    (0x0, 0x1, 0x2, 0x3, 0x4, 0x5, 0x6, 0xD, 0xC, 0xB, 0xA, 0x9, 0x8, 0x7, 0xF, 0xE),
    (0x0, 0x1, 0x2, 0x3, 0x4, 0x5, 0x6, 0x7, 0xE, 0xD, 0xC, 0xB, 0xA, 0x9, 0x8, 0xF),
    (0x0, 0x1, 0x2, 0x3, 0x4, 0x5, 0x6, 0x7, 0xF, 0xE, 0xD, 0xC, 0xB, 0xA, 0x9, 0x8),
)

zone_tbl = ( 0, 1, 2, 3, 4, 5, 6, 7, 1, 2, 3, 4, 5, 6, 7, 8 )

track_zone_tbl = (
    (0x000, 0x09E, 0x13C, 0x1D1, 0x266, 0x2FB, 0x390, 0x425),
    (0x091, 0x12F, 0x1C4, 0x259, 0x2EE, 0x383, 0x418, 0x48A),
)

class Disk_Sys:
    def __init__(self, d: bytearray):
        self.raw = d[:232]
        self.reload()
    
    def reload(self):
        """
        Reload System Data based from current RAW data.
        """
        self.region = read_32(self.raw, 0)
        self.fmt_type = self.raw[4]
        self.disk_type = self.raw[5] - self.raw[4]
        self.ipl_load_size = read_16(self.raw, 6)
        self.ipl_load_addr = read_32(self.raw, 0x1C)
        self.rom_end_lba = read_16(self.raw, 0xE0)
        self.ram_start_lba = read_16(self.raw, 0xE2)
        self.ram_end_lba = read_16(self.raw, 0xE4)

        # check defect track info
        if self.is_defect_info_valid() == False: raise Exception("Disk Defect info in System Data is not valid.")

        # get all defect tracks info (pzone)
        self.defect_tracks = []
        self.defect_tracks.append(self.raw[0x20:][:self.raw[8]])
        for i in range(1, 16):
            self.defect_tracks.append(self.raw[0x20+self.raw[8:][i-1]:][:self.raw[8:][i] - self.raw[8:][i-1]])
    
    def update(self, defect=True, d64=False):
        """
        Update RAW data based from variables.
        """
        raw = bytearray(232)

        write_32(raw, 0x00, self.region)
        raw[0x04] = self.fmt_type
        raw[0x05] = self.fmt_type + self.disk_type
        write_16(raw, 0x06, self.ipl_load_size)
        write_32(raw, 0x1C, self.ipl_load_addr)
        write_16(raw, 0xE0, self.rom_end_lba)
        write_16(raw, 0xE2, self.ram_start_lba)
        write_16(raw, 0xE4, self.ram_end_lba)

        if d64 == False:
            write_32(raw, 0x18, 0xFFFFFFFF)
            write_16(raw, 0xE8, 0xFFFF)

        if defect == True and d64 == False:
            # add defect data back
            j = 0
            for i in range(16):
                for k in self.defect_tracks[i]:
                    raw[0x20+j] = k
                    j += 1
                raw[0x08+i] = j
        
        self.raw = raw
    
    def is_defect_info_valid(self) -> bool:
        """
        Check if the Disk defect information is valid.
        """
        # check if all offset info is 0
        if all([self.raw[0x08:0x18][i] == 0 for i in range(len(self.raw[0x08:0x18]))]) == True: return True
        # check if all offset info is lower than each other
        if all([self.raw[i-1] < self.raw[i] for i in range(0x08+1, 0x18)]) == False: return False
        # check if all defect track info is lower than each other
        defect_tracks = []
        defect_tracks.append(self.raw[0x20:][:self.raw[8]])
        for i in range(1, 16):
            defect_tracks.append(self.raw[0x20+self.raw[8:][i-1]:][:self.raw[8:][i] - self.raw[8:][i-1]])
        for j in defect_tracks:
            if all([j[i-1] < j[i] for i in range(1, len(j))]) == False: return False
        return True
    
    def is_info_valid(self, d64=False) -> bool:
        """
        Check if the loaded Disk System Data information is valid.
        (Does not check LBA formatting info as development disk dumps do not have this information.)
        """
        if d64 == False:
            # check region (JPN, USA, DEV)
            if self.region != 0xE848D316 and self.region != 0x2263EE56 and self.region != 0x00000000: return False
            # check format type
            if self.fmt_type != 0x10: return False
        # check disk type
        if self.disk_type < 0 or self.disk_type > 6: return False
        # check ipl load size (can't be more than 0x800000 bytes)
        if self.ipl_load_size > 438: return False
        # check ipl load addr
        if self.ipl_load_addr < 0x80000000 or self.ipl_load_addr >= 0x80800000: return False
        return True

    def is_lba_info_valid(self) -> bool:
        """
        Check if the LBA formatting info from the loaded Disk System data is valid.
        """
        # check rom end lba
        if self.rom_end_lba + sys_lba_count >= ram_lba_start_tbl[self.disk_type]: return False
        # check ram start/end lba
        if self.ram_start_lba == 0xFFFF and self.ram_end_lba == 0xFFFF: return True
        if self.ram_start_lba + sys_lba_count < ram_lba_start_tbl[self.disk_type]: return False
        if self.ram_end_lba + sys_lba_count < ram_lba_start_tbl[self.disk_type]: return False
        if self.ram_start_lba + sys_lba_count > lba_count: return False
        if self.ram_end_lba + sys_lba_count > lba_count: return False
        return True

    def is_ram_lba_info_present(self) -> bool:
        """
        Check if the RAM LBA info exists or not.
        """
        if self.ram_start_lba == 0xFFFF and self.ram_end_lba == 0xFFFF: return False
        return True


class Disk_Id:
    def __init__(self, d: bytearray):
        self.raw = d[:232]

        self.initial_code = d[:4].decode("ASCII")
        self.game_version = d[4]
        self.disk_number = d[5]
        self.ram_use = d[6]
        self.disk_use = d[7]
        self.factory_line = d[8:][:8]
        self.production_time = d[0x10:][:8]
        self.company_code = d[0x18:][:2].decode("ASCII")
        self.free_area = d[0x1A:][:6]


class PhysInfo:
    def __init__(self, h: int, t: int, b: int):
        self.head = h
        self.track = t
        self.block = b
    
    def get_zone(self) -> int:
        """
        Returns Disk Zone information.
        """
        zone = 0
        for i in range(8):
            if self.track >= track_zone_tbl[0][i]:
                zone = i
            else:
                break
        return int(zone + self.head)

# LBA to VZone (disktype, lba)
def lba_to_vzone(t: int, lba: int) -> int:
    """
    Returns Virtual Zone information based from Disk Type and LBA.
    """
    vzone = 0

    for i in reversed(range(16)):
        if lba < vzone_lba_tbl[t][i]:
            vzone = i
        else:
            break
    return int(vzone)

# VZone to PZone (disktype, vzone)
def vzone_to_pzone(t: int, vzone: int) -> int:
    """
    Returns Physical Zone information based from Disk Type and Virtual Zone.
    """
    return int(pzone_tbl[t][vzone])

# PZone to Disk Zone (pzone)
def pzone_to_zone(vzone: int) -> int:
    """
    Returns Disk Physical Zone information (regardless of side) based from Physical Zone.
    """
    return int(zone_tbl[vzone])

# Block Size of LBA (disktype, lba)
def size_of_lba(t: int, lba: int) -> int:
    """
    Returns the block byte size of any given LBA on any given Disk Type.
    """
    return int(block_size_per_pzone[pzone_to_zone(vzone_to_pzone(t, lba_to_vzone(t, lba)))])

# Sector Size of LBA (disktype, lba)
def size_of_sectors(t: int, lba: int) -> int:
    """
    Returns the sector byte size of any given LBA on any given Disk Type.
    """
    return int(size_of_lba(t, lba) / sector_count)

# Size of LBAs (disktype, first LBA, LBA amount)
def lba_to_byte(t: int, start_lba: int, nlba: int) -> int:
    """
    Returns the byte size of any given LBA and n amount of blocks from it on any given Disk Type.
    """
    if (start_lba >= lba_count): raise ValueError()
    if (start_lba + nlba > lba_count): raise ValueError()
    return int(sum([size_of_lba(t, i) for i in range(start_lba, start_lba + nlba)]))

# LBA amount from byte size (disktype, first LBA, byte amount)
def byte_to_lba(t: int, start_lba: int, nbytes: int) -> int:
    """
    Returns the size in LBA blocks of any given LBA and n amount of bytes from it on any given Disk Type.
    """
    for i in range(start_lba, lba_count):
        nbytes -= size_of_lba(t, i)
        if (nbytes <= 0): return int(i - start_lba)
    raise ValueError()

def read_16(b, offset):
    """
    Read 16-bit unsigned big endian from array and offset.
    """
    return struct.unpack(">H", b[offset:][:2])[0]

def read_32(b, offset):
    """
    Read 32-bit unsigned big endian from array and offset.
    """
    return struct.unpack(">I", b[offset:][:4])[0]

def write_16(b, offset, value):
    """
    Write 16-bit unsigned big endian to array and offset.
    """
    struct.pack_into(">H", b, offset, value)

def write_32(b, offset, value):
    """
    Write 32-bit unsigned big endian to array and offset.
    """
    struct.pack_into(">I", b, offset, value)

def verify_sec_repeat_block(d: bytearray, secsize: int) -> bool:
    """
    Compares all sectors in a given block of data and sector size and returns True if they are all identical to each other. If not, returns False.
    """
    comp = d[:secsize]
    # compare all sectors if they're identical or not
    for i in range(1, sector_count):
        if (all([comp == d[i*secsize:][:secsize]]) == False): return False
    return True

def lba_to_phys(sys: Disk_Sys, lba: int) -> PhysInfo:
    """
    Returns physical disk geometry information based from provided Disk System Data Formatting information and LBA.
    """
    if lba < 0 or lba >= lba_count: raise ValueError()

    # get block info
    if ((int(lba) & 3) == 0) or ((int(lba) & 3) == 3):
        r_block = int(0)
    else:
        r_block = int(1)

    vzone = lba_to_vzone(sys.disk_type, lba)
    pzone = vzone_to_pzone(sys.disk_type, vzone)

    # get head info
    r_head = int(pzone / 8)

    # get zone
    zone = int(pzone - (7 * r_head))

    # get start lba of vzone
    vzone_start_lba = 0
    if vzone > 0: vzone_start_lba = vzone_lba_tbl[sys.disk_type][vzone - 1]

    # get current track of vzone
    r_track = int((lba - vzone_start_lba) / 2)

    # get start/end track of zone
    pzone_start_track = int(track_zone_tbl[0][zone - r_head])

    # count from the opposite side if head 1
    if r_head == 1: r_track = -r_track
    r_track += track_zone_tbl[r_head][zone - r_head]

    # skip defective tracks
    for i in sys.defect_tracks[pzone]:
        if (pzone_start_track + i) > r_track: break
        r_track += 1

    return PhysInfo(r_head, r_track, r_block)
