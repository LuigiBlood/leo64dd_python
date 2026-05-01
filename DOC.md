# leo64dd.py

This library handles the basics of 64DD disk calculations, as well as other utilities.

## Classes
### Disk_Sys

This class is for an easier access of the System Data information of the disk, as well as utilities in relation to its data.

- `Disk_Sys.raw`: RAW bytearray.
- `Disk_Sys.region`: Either `E848D316` (Japan), `2263EE56` (USA), `00000000` (Development / None)
- `Disk_Sys.fmt_type`: Either `0x10` or `0x00` (D64 file format only)
- `Disk_Sys.disk_type`: Between `0` and `6` included. **Determines disk block logic and data block order, and is important for 64DD disk block calculations.**
- `Disk_Sys.ipl_load_size`: Amount of blocks to load from ROM Area (starting from LBA 24) to the entrypoint RAM address.
- `Disk_Sys.ipl_load_addr`: Entrypoint RAM Address.
- `Disk_Sys.rom_end_lba`: End of written ROM Area block (base LBA = 24) (Used in D64 format and Retail Disk dumps.)
- `Disk_Sys.ram_start_lba`: Start of written RAM Area block (base LBA = 24), `0xFFFF` if not used. (Used in D64 format and Retail Disk dumps.)
- `Disk_Sys.ram_end_lba`: End of written RAM Area block (base LBA = 24), `0xFFFF` if not used. (Used in D64 format and Retail Disk dumps.)
- `Disk_Sys.defect_tracks[][]`: List of defective physical cylinders/tracks. Only relevant for MAME file format management.


- `Disk_Sys(bytearray)`: Initialize class with bytearray of System Data.
- `Disk_Sys.reload()`: Reloads variables from RAW bytearray initially given.
- `Disk_Sys.update(defect, d64)`: Modify RAW bytearray using the variables.
	- `defect`: bool, injects defect tracks information. (default: `True`)
	- `d64`: bool, D64 file format (default: `False`)
- `Disk_Sys.is_defect_info_valid()`: Checks disk defect information from RAW bytearray. `False` if invalid, `True` if valid.
- `Disk_Sys.is_info_valid(d64)`: Check if the loaded Disk System Data information is valid. (Does not check LBA formatting info as development disk dumps do not have this information.) `False` if invalid, `True` if valid.
	- `d64`: bool, D64 file format (default: `False`)
- `Disk_Sys.is_lba_info_valid()`: Check if the LBA formatting info from the loaded Disk System data is valid. `False` if invalid, `True` if valid.
- `Disk_Sys.is_ram_lba_info_present()`: Check if the RAM LBA info exists or not. `False` if not existing, `True` if exists.

### Disk_Id

This class is for an easier access of the Disk ID block.

- `Disk_Id.raw`: RAW bytearray.
- `Disk_Id.initial_code`: ASCII encoded Disk Code. For example `DMPJ`, `EFZE`. (4 bytes)
- `Disk_Id.game_version`: Revision of the game. (1 byte)
- `Disk_Id.disk_number`: Number of the disk if the title uses several ones. (No game uses this.) (1 byte)
- `Disk_Id.ram_use`: `0x01` if MFS is used for the RAM Area. `0x00` if not. (1 byte)
- `Disk_Id.disk_use`: Documentation says `0x00` for Game Disk, but no other information is known. (1 byte)
- `Disk_Id.factory_line`: Factory Line Number, or `PTN64` if written from Partner-N64 to development disk. (8 bytes)
- `Disk_Id.production_time`: BCD Timestamp of production `00YYYYMMDDHHMMSS` (8 bytes)
- `Disk_Id.company_code`: ASCII Company Code. `01` = Nintendo. (2 bytes)
- `Disk_Id.free_area`: Can be used as developers sees fit. (6 bytes)


- `Disk_Id(bytearray)`: Initialize class with bytearray of Disk ID.
- `Disk_Id.reload()`: Reloads variables from RAW bytearray initially given.
- `Disk_Id.update()`: Modify RAW bytearray using the variables.
- `Disk_Id.remove_disk_unique_info()`: Remove Factory Line and Production Time info.

### PhysInfo

This class is for managing physical disk geometry locations from disk. This is only relevant for low level use.

- `PhysInfo(head, track, block)`: Initializes class with head (side), track (cylinder) and block (0 or 1).
- `PhysInfo.get_zone()`: Gets zone based from provided information at initialization.

## Functions

### Low Level Information
- `lba_to_vzone(disk_type, lba)`: Returns Virtual Zone information based from Disk Type and LBA.
- `vzone_to_pzone(disk_type, vzone)`: Returns Physical Zone information based from Disk Type and Virtual Zone.
- `pzone_to_zone(vzone)`: Returns Disk Physical Zone information (regardless of side) based from Physical Zone.

- `verify_sec_repeat_block(bytearray, sector_size)`: Compares all sectors in a given block of data and sector size and returns True if they are all identical to each other. If not, returns False.
- `lba_to_phys(Disk_Sys, lba)`: Returns physical disk geometry location based from provided Disk System Data Formatting information and LBA. (Returns `PhysInfo`)

### High Level Information
This is the stuff you should use.

- `size_of_lba(disk_type, lba)`: Returns the block byte size of any given LBA on any given Disk Type.
- `size_of_sectors(disk_type, lba)`: Returns the sector byte size of any given LBA on any given Disk Type.
- `lba_to_byte(disk_type, start_lba, nlba)`: Returns the byte size from any given start LBA and n amount of blocks from it on any given Disk Type.
- `byte_to_lba(disk_type, start_lba, nbytes)`: Returns the size in LBA blocks from any given LBA and n amount of bytes from it on any given Disk Type.

# leo64ddfile.py

## Usage as an application
    Usage: leo64ddfile.py <toformat> base_file out_file
     <toformat> = ndd  (NDD disk image format)
                = mame (MAME/ares physical disk image format)
                = d64  (D64 master disk image format, lossy process

## Classes

These classes were made to manage all relevant 64DD disk file formats in a transparent manner.

- `Disk_NDD`: NDD file format class
  - Common format from 64DD Disk Dumper, snapshot of disk based from libleo block ordering.
- `Disk_MAME`: MAME file format class
  - Format used for MAME, based from physical block ordering.
- `Disk_D64`: D64 file format class
  - Master Disk Format used by the official Nintendo 64 Software Development Kit. Does not contain disk specific information.

### Definitions
Each of the classes have the following:

- `class.sys_data`: Contains Disk_Sys class based from provided disk file.
- `class.disk_id`: Contains Disk_Id class based from provided disk file.
- `class.raw`: Contains raw file data.
- `class.development`: `False` if disk file is Retail format, `True` if disk file is Development format.

The following is for initializing the class.
- `class.load(bytearray)`: Provide bytearray of file, checks validity and then initializes everything.
- `class.convert(disk_class)`: Provide any of the aforementioned classes and convert all information according to the class type calling it.

In both cases, the variable needs to be initialized with one of the disk classes and then call either of them.

The following is for finding blocks.
- `class.get_lba_offset(lba)`: Provide LBA and it will return the raw file address to the data.
- `class.get_lba(lba, makesys=False)`: Provide LBA and it will return a bytearray of the entire block.
  - `makesys` is only for `Disk_D64` class, and is not required, and adds information to the System Data to look more like a Retail disk. (default=`False`)

## High Level Functions
The following is for a general transparent use of the disk files:
- `basic_disk_file_check(bytearray)`: Provide bytearray of the full disk file and returns the format. Either `ndd`, `mame` or `d64`.
- `load_disk_file(bytearray)`: Provide bytearray of the full disk file and returns fully loaded disk class.
