#
#   64DD File Module + Conversion
#

import sys, leo64dd

size_format_ndd = 0x3DEC800
size_format_mame = 0x435B0C0

# declare classes in advance because each of them can work with each other
class Disk_NDD: pass
class Disk_MAME: pass
class Disk_D64: pass

# NDD format class
class Disk_NDD:
    def load(self, d: bytearray):
        # check size of NDD file
        if len(d) != size_format_ndd: raise Exception("Wrong size of NDD file")

        # find good retail sys block
        sys_lba = -1
        for i in leo64dd.sys_lba_tbl_retail:
            block = d[leo64dd.lba_to_byte(0, 0, i):][:leo64dd.size_of_lba(0, i)]
            if leo64dd.verify_sec_repeat_block(block, 0xE8):
                sys_data = leo64dd.Disk_Sys(block)
                if sys_data.is_info_valid() == False: continue
                if sys_data.is_defect_info_valid() == False: continue
                sys_lba = i
                self.sys_data = sys_data
                self.development = False
                break
        
        # find good dev sys block (if retail not found, else don't bother)
        for i in leo64dd.sys_lba_tbl_dev:
            if sys_lba != -1: break
            block = d[leo64dd.lba_to_byte(0, 0, i):][:leo64dd.size_of_lba(0, i)]
            if leo64dd.verify_sec_repeat_block(block, 0xC0):
                sys_data = leo64dd.Disk_Sys(block)
                if sys_data.is_info_valid() == False: continue
                if sys_data.is_defect_info_valid() == False: continue
                sys_lba = i
                self.sys_data = sys_data
                self.development = True
                break
        
        # if still not found then error
        if sys_lba == -1: raise Exception("Cannot find valid Disk System Data")

        # find good disk id block
        diskid_lba = -1
        for i in leo64dd.sys_lba_tbl_diskid:
            block = d[leo64dd.lba_to_byte(self.sys_data.disk_type, 0, i):][:leo64dd.size_of_lba(self.sys_data.disk_type, i)]
            if leo64dd.verify_sec_repeat_block(block, 0xE8):
                diskid_lba = i
                self.disk_id = leo64dd.Disk_Id(block)
                break
        
        # if still not found then error
        if diskid_lba == -1: raise Exception("Cannot find valid Disk ID Data")

        self.raw = d

    def convert(self, disk):
        if type(disk) is Disk_MAME:
            # set everything
            self.raw = bytearray(size_format_ndd)
            self.sys_data = disk.sys_data
            self.disk_id = disk.disk_id
            self.development = disk.development
            # copy each block one by one
            for i in range(leo64dd.lba_count):
                position = self.get_lba_offset(i)
                size = leo64dd.size_of_lba(disk.sys_data.disk_type, i)
                self.raw[position:position+size] = disk.get_lba(i)
        elif type(disk) is Disk_D64:
            # set everything
            self.raw = bytearray(size_format_ndd)
            self.sys_data = disk.sys_data
            self.disk_id = disk.disk_id
            self.development = disk.development
            # copy each block one by one
            for i in range(leo64dd.lba_count):
                position = self.get_lba_offset(i)
                size = leo64dd.size_of_lba(disk.sys_data.disk_type, i)
                self.raw[position:position+size] = disk.get_lba(i, makesys=True)
        elif type(disk) is Disk_NDD:
            raise Exception("Converting with identical disk object.")
        else:
            raise Exception("Converting with unknown disk object.")


    def get_lba_offset(self, lba: int) -> int:
        return leo64dd.lba_to_byte(self.sys_data.disk_type, 0, lba)
    
    def get_lba(self, lba: int) -> bytearray:
        return self.raw[self.get_lba_offset(lba):][:leo64dd.size_of_lba(self.sys_data.disk_type, lba)]
    
class Disk_MAME:
    mame_offset_table = (0x0,      0x5F15E0, 0xB79D00, 0x10801A0,0x1523720,0x1963D80,0x1D414C0,0x20BBCE0,
                         0x23196E0,0x28A1E00,0x2DF5DC0,0x3299340,0x36D99A0,0x3AB70E0,0x3E31900,0x4149200)
    
    def load(self, d: bytearray):
        # check size of MAME file
        if len(d) != size_format_mame: raise Exception("Wrong size of MAME file")

        # find good retail sys block
        sys_lba = -1
        for i in leo64dd.sys_lba_tbl_retail:
            block = d[leo64dd.lba_to_byte(0, 0, i):][:leo64dd.size_of_lba(0, i)]
            if leo64dd.verify_sec_repeat_block(block, 0xE8):
                sys_data = leo64dd.Disk_Sys(block)
                if sys_data.is_info_valid() == False: continue
                if sys_data.is_defect_info_valid() == False: continue
                sys_lba = i
                self.sys_data = sys_data
                self.development = False
                break
        
        # find good dev sys block (if retail not found, else don't bother)
        for i in leo64dd.sys_lba_tbl_dev:
            if sys_lba != -1: break
            block = d[leo64dd.lba_to_byte(0, 0, i):][:leo64dd.size_of_lba(0, i)]
            if leo64dd.verify_sec_repeat_block(block, 0xC0):
                sys_data = leo64dd.Disk_Sys(block)
                if sys_data.is_info_valid() == False: continue
                if sys_data.is_defect_info_valid() == False: continue
                sys_lba = i
                self.sys_data = sys_data
                self.development = True
                break
        
        # if still not found then error
        if sys_lba == -1: raise Exception("Cannot find valid Disk System Data")

        # find good disk id block
        diskid_lba = -1
        for i in leo64dd.sys_lba_tbl_diskid:
            block = d[leo64dd.lba_to_byte(self.sys_data.disk_type, 0, i):][:leo64dd.size_of_lba(self.sys_data.disk_type, i)]
            if leo64dd.verify_sec_repeat_block(block, 0xE8):
                diskid_lba = i
                self.disk_id = leo64dd.Disk_Id(block)
                break
        
        # if still not found then error
        if diskid_lba == -1: raise Exception("Cannot find valid Disk ID Data")

        self.raw = d
    
    def convert(self, disk):
        if type(disk) is Disk_NDD:
            # set everything
            self.raw = bytearray(size_format_mame)
            self.sys_data = disk.sys_data
            self.disk_id = disk.disk_id
            self.development = disk.development
            # copy each block one by one
            for i in range(leo64dd.lba_count):
                position = self.get_lba_offset(i)
                size = leo64dd.size_of_lba(disk.sys_data.disk_type, i)
                self.raw[position:position+size] = disk.get_lba(i)
        elif type(disk) is Disk_D64:
            # set everything
            self.raw = bytearray(size_format_mame)
            self.sys_data = disk.sys_data
            self.disk_id = disk.disk_id
            self.development = disk.development
            # copy each block one by one
            for i in range(leo64dd.lba_count):
                position = self.get_lba_offset(i)
                size = leo64dd.size_of_lba(disk.sys_data.disk_type, i)
                self.raw[position:position+size] = disk.get_lba(i, makesys=True)
        elif type(disk) is Disk_MAME:
            raise Exception("Converting with identical disk object.")
        else:
            raise Exception("Converting with unknown disk object.")
    
    def get_lba_offset(self, lba: int) -> int:
        # calculate physical geometry data and zone information
        phys = leo64dd.lba_to_phys(self.sys_data, lba)
        zone = phys.get_zone()
        # calculate track info relative to the start of the zone
        trackRelative = phys.track - leo64dd.track_zone_tbl[0][zone - phys.head]
        # calculate offset
        offset = self.mame_offset_table[(zone - phys.head) + (phys.head * 8)]
        offset += leo64dd.block_size_per_pzone[zone] * 2 * trackRelative
        offset += phys.block * leo64dd.block_size_per_pzone[zone]
        return int(offset)
    
    def get_lba(self, lba: int) -> bytearray:
        offset = self.get_lba_offset(lba)
        return self.raw[offset:][:leo64dd.size_of_lba(self.sys_data.disk_type, lba)]

class Disk_D64:
    def load(self, d: bytearray):
        # check system data
        self.sys_data = leo64dd.Disk_Sys(d[:0xE8])
        if self.sys_data.is_info_valid(d64=True) == False: raise Exception("Disk System Data is invalid.")
        self.disk_id = leo64dd.Disk_Id(d[0x100:][:0xE8])
        self.development = True

        # check size of D64 file
        size = 0x200
        size += leo64dd.lba_to_byte(self.sys_data.disk_type, leo64dd.sys_lba_count, self.sys_data.rom_end_lba + 1)
        if self.sys_data.ram_start_lba != 0xFFFF and self.sys_data.ram_end_lba != 0xFFFF:
            size += leo64dd.lba_to_byte(self.sys_data.disk_type, leo64dd.sys_lba_count + self.sys_data.ram_start_lba, self.sys_data.ram_end_lba - self.sys_data.ram_start_lba + 1)
        if len(d) != size: raise Exception("Wrong size of D64 file")

        self.raw = d

    def convert(self, disk):
        if type(disk) is Disk_NDD or type(disk) is Disk_MAME:
            # copy info
            self.sys_data = disk.sys_data
            self.disk_id = disk.disk_id
            self.development = disk.development

            # remove unnecessary system data
            self.sys_data.fmt_type = 0x00
            self.sys_data.region = 0x00000000

            if self.sys_data.is_lba_info_valid() == False:
                # make new lba formatting info if wrong
                self.sys_data.rom_end_lba = leo64dd.ram_lba_start_tbl[self.sys_data.disk_type] - leo64dd.sys_lba_count - 1
                if self.sys_data.disk_type == 6:
                    self.sys_data.ram_start_lba = 0xFFFF
                    self.sys_data.ram_end_lba = 0xFFFF
                else:
                    self.sys_data.ram_start_lba = leo64dd.ram_lba_start_tbl[self.sys_data.disk_type] - leo64dd.sys_lba_count
                    self.sys_data.ram_end_lba = leo64dd.lba_count - leo64dd.sys_lba_count - 1
            
            # update raw sys data
            self.sys_data.update(defect=False, d64=True)

            # calculate D64 file size
            size = 0x200
            size += leo64dd.lba_to_byte(self.sys_data.disk_type, leo64dd.sys_lba_count, self.sys_data.rom_end_lba + 1)
            if self.sys_data.is_ram_lba_info_present() == True:
                size += leo64dd.lba_to_byte(self.sys_data.disk_type, leo64dd.sys_lba_count + self.sys_data.ram_start_lba, self.sys_data.ram_end_lba - self.sys_data.ram_start_lba + 1)

            # make new raw data
            self.raw = bytearray(size)
            # add sys_data
            self.raw[0x000:0x0E8] = self.sys_data.raw
            # add disk_id
            self.raw[0x100:0x1E8] = self.disk_id.raw
            # add ROM area
            for i in range(self.sys_data.rom_end_lba + 1):
                position = self.get_lba_offset(leo64dd.sys_lba_count + i)
                size = leo64dd.size_of_lba(disk.sys_data.disk_type, leo64dd.sys_lba_count + i)
                self.raw[position:position+size] = disk.get_lba(leo64dd.sys_lba_count + i)
            # add RAM area
            if self.sys_data.is_ram_lba_info_present() == True:
                for i in range(self.sys_data.ram_start_lba, self.sys_data.ram_end_lba + 1):
                    position = self.get_lba_offset(leo64dd.sys_lba_count + i)
                    size = leo64dd.size_of_lba(disk.sys_data.disk_type, leo64dd.sys_lba_count + i)
                    self.raw[position:position+size] = disk.get_lba(leo64dd.sys_lba_count + i)
        elif type(disk) is Disk_D64:
            raise Exception("Converting with identical disk object.")
        else:
            raise Exception("Converting with unknown disk object.")
            

    def get_lba_offset(self, lba: int) -> int:
        if lba in leo64dd.sys_lba_tbl_retail:
            # retail System Data
            return 0x000
        elif lba in leo64dd.sys_lba_tbl_dev:
            # development System Data
            return 0x000
        elif lba in leo64dd.sys_lba_tbl_diskid:
            # Disk ID
            return 0x100
        elif lba >= leo64dd.sys_lba_count and lba <= (leo64dd.sys_lba_count + self.sys_data.rom_end_lba):
            # ROM Area (only within the allocated ROM Area)
            return 0x200 + leo64dd.lba_to_byte(self.sys_data.disk_type, leo64dd.sys_lba_count, lba - leo64dd.sys_lba_count)
        elif self.sys_data.is_ram_lba_info_present() == True and lba >= (leo64dd.sys_lba_count + self.sys_data.ram_start_lba) and lba <= (leo64dd.sys_lba_count + self.sys_data.ram_end_lba):
            # RAM Area (only within the allocated RAM Area)
            offset = 0x200
            offset += leo64dd.lba_to_byte(self.sys_data.disk_type, leo64dd.sys_lba_count, self.sys_data.rom_end_lba + 1)
            offset += leo64dd.lba_to_byte(self.sys_data.disk_type, leo64dd.sys_lba_count + self.sys_data.ram_start_lba, lba - leo64dd.sys_lba_count - self.sys_data.ram_start_lba)
            return offset
        return -1
    
    def get_lba(self, lba: int, makesys=False) -> bytearray:
        offset = self.get_lba_offset(lba)
        if offset == 0x000:
            data = bytearray(leo64dd.block_size_per_pzone[0])
            if self.development == False: secsize = 0xE8
            else: secsize = 0xC0
            sector = self.raw[:secsize]
            if makesys == True:
                if lba in leo64dd.sys_lba_tbl_retail:
                    sector[0x00:0x04] = (0xE8, 0x48, 0xD3, 0x16)
                sector[0x04] = 0x10
                sector[0x05] += 0x10
                sector[0x18:0x1C] = (0xFF, 0xFF, 0xFF, 0xFF)
                if self.development == False:
                    sector[0xE6:0xE8] = (0xFF, 0xFF)
            for i in range(leo64dd.sector_count):
                data[i*secsize:(i+1)*secsize] = sector
            return data
        elif offset == 0x100:
            data = bytearray(leo64dd.block_size_per_pzone[0])
            secsize = 0xE8
            for i in range(leo64dd.sector_count):
                data[i*secsize:(i+1)*secsize] = self.raw[0x100:0x100+secsize]
            return data
        elif offset >= 0x200:
            return self.raw[offset:][:leo64dd.size_of_lba(self.sys_data.disk_type, lba)]
        else:
            return bytearray(leo64dd.size_of_lba(self.sys_data.disk_type, lba))

def basic_disk_file_check(d: bytearray) -> str:
    if len(d) == size_format_ndd: return "ndd"
    elif len(d) == size_format_mame: return "mame"
    elif len(d) >= (0x200 + 0x4D08) and len(d) <= (0x200 + 0x3D78F40): return "d64"
    else: return "none"

def load_disk_file(d: bytearray):
    chk = basic_disk_file_check(d)
    if chk == "ndd":
        test = Disk_NDD()
        test.load(d)
        print("Disk is NDD format.")
    elif chk == "mame":
        test = Disk_MAME()
        test.load(d)
        print("Disk is MAME format.")
    elif chk == "d64":
        test = Disk_D64()
        test.load(d)
        print("Disk is D64 format.")
    else:
        print("This is not a disk file.")
        raise Exception("This is not a disk file.")
    return test

if __name__ == '__main__':
    if (len(sys.argv) != 4):
        print(f"Usage: {sys.argv[0]} <toformat> base_file ndd_file")
        print(" <toformat> = ndd  (NDD disk image format)")
        print("            = mame (MAME/Ares physical disk image format)")
        print("            = d64  (D64 master disk image format, lossy process)")
    else:
        if sys.argv[1] != "ndd" and sys.argv[1] != "mame" and sys.argv[1] != "d64":
            print(f"Unknown \" {sys.argv[1]} \" format to convert to.")
            sys.exit(2)
        
        with open(sys.argv[2], "rb") as infile:
            disk_img = bytearray(infile.read())
        disk_obj = load_disk_file(disk_img)

        if sys.argv[1] == "ndd":
            # To Disk_NDD
            if type(disk_obj) is Disk_NDD:
                print("Disk is already NDD format, cancelling.")
                sys.exit(1)
            print("Converting to NDD format...")
            after = Disk_NDD()
        elif sys.argv[1] == "mame":
            # To Disk_MAME
            if type(disk_obj) is Disk_MAME:
                print("Disk is already MAME format, cancelling.")
                sys.exit(1)
            print("Converting to MAME format...")
            after = Disk_MAME()
        elif sys.argv[1] == "d64":
            # To Disk_D64
            if type(disk_obj) is Disk_D64:
                print("Disk is already D64 format, cancelling.")
                sys.exit(1)
            print("Converting to D64 format...")
            after = Disk_D64()
        
        after.convert(disk_obj)
        print("Conversion done. Writing file...")
        with open(sys.argv[3], "wb") as outfile:
            outfile.write(after.raw)
        print("Complete.")
        sys.exit(0)
