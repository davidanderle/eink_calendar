import sys
# TODO: This creates a dependency forthe ESP32 platform
if sys.platform == "esp32":
    import pros3
    from machine import Pin, SPI
if sys.platform == "win32":
    from unittest.mock import Mock
    class SPI: pass
    class Pin: pass

class RegisterBase:
    USB         = 0x4E00
    I2C         = 0x4C00
    IMAGE_PROC  = 0x4600
    JPG         = 0x4000
    GPIO        = 0x1E00
    HS_UART     = 0x1C00
    INTC        = 0x1400
    DISP_CTRL   = 0x1000
    SPI         = 0x0E00
    THERM       = 0x0800
    SD_CARD     = 0x0600
    MEMORY_CONV = 0x0200
    SYSTEM      = 0x0000
    
# IT8951 register memory map
class Register:
    # Engine width/height register
    LUT0EWHR  = RegisterBase.DISP_CTRL + 0x000
    # LUT0 XY register
    LUT0XYR   = RegisterBase.DISP_CTRL + 0x040
    # LUT0 Base Address Reg
    LUT0BADDR = RegisterBase.DISP_CTRL + 0x080
    # LUT0 Mode and Frame number Reg
    LUT0MFN   = RegisterBase.DISP_CTRL + 0x0C0 
    # LUT0 and LUT1 Active Flag Reg
    LUT01AF   = RegisterBase.DISP_CTRL + 0x114 
    # Update parameter0 setting reg
    UP0SR     = RegisterBase.DISP_CTRL + 0x134
    # Update parameter1 setting reg
    UP1SR     = RegisterBase.DISP_CTRL + 0x138
    # LUT0 Alpha blend and fill rectangle value
    LUT0ABFRV = RegisterBase.DISP_CTRL + 0x13C
    # Update buffer base address
    UPBBADDR  = RegisterBase.DISP_CTRL + 0x17C
    # LUT0 Image buffer X/Y offset register
    LUT0IMXY  = RegisterBase.DISP_CTRL + 0x180
    # LUT Status Reg (status of All LUT Engines)
    LUTAFSR   = RegisterBase.DISP_CTRL + 0x224
    # Set BG and FG Color if Bitmap mode enable only (1bpp)
    BGVR      = RegisterBase.DISP_CTRL + 0x250

    I80CPCR   = RegisterBase.SYSTEM    + 0x004

    MCSR      = RegisterBase.MEMORY_CONV + 0x00
    LISAR     = RegisterBase.MEMORY_CONV + 0x08

class CommsMode:
    # TEST_CFG[2:0] = 0b000, I80CPCR = 0 (not supported)
    I80      = 0
    # TEST_CFG[2:0] = 0b000, I80CPCR = 1 (not supported)
    M68      = 1
    # TEST_CFG[2:0] = 0b001, I80CPCR = X
    SPI      = 2
    # TEST_CFG[2:0] = 0b110, I80CPCR = X (not supported)
    I2C_0x46 = 3
    # TEST_CFG[2:0] = 0b111, I80CPCR = X (not supported)
    I2C_0x35 = 4

# These double-words are used in an SPI frame to set their type
class SpiPreamble:
    COMMAND    = 0x6000
    WRITE_DATA = 0x0000
    READ_DATA  = 0x1000
    
class Command:
    # System running command: enable all clocks, and go to active state
    SYS_RUN         = 0x0001
    # Standby command: gate off clocks, and go to standby state
    STANDBY         = 0x0002
    # Sleep command: disable all clocks, and go to sleep state
    SLEEP           = 0x0003
    # Read register command
    REG_RD          = 0x0010
    # Write register command
    REG_WR          = 0x0011
    MEM_BST_RD_T    = 0x0012
    MEM_BST_RD_S    = 0x0013
    MEM_BST_WR      = 0x0014
    MEM_BST_END     = 0x0015
    LD_IMG          = 0x0020
    LD_IMG_AREA     = 0x0021
    LD_IMG_END      = 0x0022
    LD_IMG_1BPP     = 0x0095
    DPY_AREA        = 0x0034
    DPY_BUF_AREA    = 0x0037
    POWER_SEQUENCE  = 0x0038
    CMD_VCOM        = 0x0039
    FILL_RECT       = 0x003A
    CMD_TEMPERATURE = 0x0040
    BPP_SETTINGS    = 0x0080
    GET_DEV_INFO    = 0x0302

# Color-depth of the display to drive
class ColorDepth:
    # |P[n+7]|P[n+6]|P[n+5]|P[n+4]|P[n+3]|P[n+2]|P[n+1]|P[n+0]|
    BPP_2BIT = 0
    # |P[n+3] 0|P[n+2] 0|P[n+1] 0|P[n+0] 0|
    BPP_3BIT = 1
    # |P[n+3]|P[n+2]|P[n+1]|P[n+0]|
    BPP_4BIT = 2
    # |P[n+1]|P[n+0]|
    BPP_8BIT = 3
    BPP_1BIT = 4

    _bpp_per_byte_map = {
        BPP_1BIT: 8,
        BPP_2BIT: 4,
        BPP_3BIT: 2,
        BPP_4BIT: 2,
        BPP_8BIT: 1
    }

    _bpp_code_map = {
        1: BPP_1BIT,
        2: BPP_2BIT,
        3: BPP_3BIT,
        4: BPP_4BIT,
        8: BPP_8BIT
    }
    
    @classmethod
    def pixel_per_byte(cls, bpp: 'ColorDepth'):
        return cls._bpp_per_byte_map.get(bpp)

    @classmethod
    def bpp_to_code(cls, bpp: int):
        return cls._bpp_code_map.get(bpp)

# Rotational angle of the displayed image
class RotateMode:
    ROTATE_0   = 0
    ROTATE_90  = 1
    ROTATE_180 = 2
    ROTATE_270 = 3

class Endianness:
    LITTLE = 0
    BIG    = 1
    
# Waveform display modes are described here:
# http://www.waveshare.net/w/upload/c/c4/E-paper-mode-declaration.pdf
class DisplayMode:
    INIT  = 0
    DU    = 1
    GC16  = 2
    GL16  = 3
    GLR16 = 4
    GLD16 = 5
    A2    = 6
    DU4   = 7
    
class DeviceInfo:
    Size = 40
    def __init__(self, panel_width: int, panel_height: int, img_buff_addr: int,\
                 firmware_version: str, lut_version: str):
        self.panel_width      = panel_width
        self.panel_height     = panel_height
        self.img_buff_addr    = img_buff_addr
        self.firmware_version = firmware_version
        self.lut_version      = lut_version
    
    @classmethod
    def from_u16_words(cls, u16_words: list):
        if len(u16_words)*2 != DeviceInfo.Size:
            raise "Input must have 20 elements (40 bytes)"

        width            = u16_words[0]
        height           = u16_words[1]
        img_buff_addr    = (u16_words[3] << 16) | u16_words[2]
        firmware_version = ''.join([chr(x>>8)+chr(x&0xFF) for x in u16_words[4:12]])
        lut_version      = ''.join([chr(x>>8)+chr(x&0xFF) for x in u16_words[12:20]])

        return cls(
            width,
            height,
            img_buff_addr,
            firmware_version,
            lut_version
        )

    def __str__(self) -> str:
        return f"Panel width: {self.panel_width}\n" + \
               f"Panel height: {self.panel_height}\n" + \
               f"Image buffer address: {hex(self.img_buff_addr)}\n" + \
               f"Firmware version: {self.firmware_version}\n" + \
               f"LUT version: {self.lut_version}"

class Rectangle:
    def __init__(self, x: int, y: int, w: int, h: int):
        self.x      = x
        self.y      = y
        self.width  = w
        self.height = h

    def area(self) -> int:
        return self.width*self.height
        
    def to_list(self) -> list:
        return [self.x, self.y, self.width, self.height]
    
    def is_contained_within(self, rect: 'Rectangle') -> bool:
        return (
            self.x >= rect.x and
            self.y >= rect.y and
            self.x + self.width <= rect.x + rect.width and
            self.y + self.height <= rect.x + rect.height
        )

    def __str__(self) -> str:
        return f"(x,y): ({self.x},{self.y})\n" + \
               f"(w,h): ({self.width},{self.height})\n" + \
               f"Area: {self.area()}"

class ImageInfo:
    def __init__(self, endian: Endianness, bpp: ColorDepth, rotation: RotateMode):
        self.endianness = endian
        self.bpp        = bpp
        self.rotation   = rotation

    def pack_to_u16(self) -> int:
        return (self.endianness << 8) | (self.bpp << 4) | self.rotation

# For the SPI protocol description, refer to 
# https://www.waveshare.net/w/upload/1/18/IT8951_D_V0.2.4.3_20170728.pdf and
# https://v4.cecdn.yun300.cn/100001_1909185148/IT8951_I80+ProgrammingGuide_16bits_20170904_v2.7_common_CXDX.pdf
class it8951:
    def __init__(self, spi: SPI, ncs: Pin, hrdy: Pin, vcom_mV):
        """
        Args:
            spi: Initialised SPI channel with SCLK <24MHz.
            ncs: Initialised GPIO for the nCS output pin
            hrdy: Initialised GPIO for the HRDY input pin
            vcom_mV: [Optional] Note that the IT8951 development
            boards ship with waveforms that are tuned to a specific vcom voltage.
            Therefore setting this may mess up the drawn pixels.
        """
        # There are 2 hardware SPI channels on the ESP32 and they can be mapped
        # to any pin, however, they are limited to 40MHz if not used on the 
        # default ones. The IT8951's maximum SPI speed is 24MHz either way, so 
        # we're good. The data must be clocked out MSB first at SPI Mode 0 or 3 
        # (0 used). At 24MHz a full refresh should take about <450ms
        self._spi = spi
        # Active-low chip select
        self._ncs = ncs
        # Host-ready pin (toggled by the IT8951)
        self._hrdy = hrdy

        if sys.platform != "win32":
            print("Initialising IT8951...")
            self.device_info = self.get_device_info()

            if self.device_info.panel_height == 0 or self.device_info.panel_width == 0:
                raise Exception("Failed to establish communication with the IT8951")

            self.set_img_buff_base_address(self.device_info.img_buff_addr)
            self.set_i80_packed_mode(True)

            print(self.device_info)
            self.panel_area = Rectangle(0, 0, self.device_info.panel_width, self.device_info.panel_height)

            rxvcom_mV = self.get_vcom()
            print(f"Current VCOM = {rxvcom_mV/1000}")

            if vcom_mV is not None and vcom_mV != rxvcom_mV:
                print(f"Settig VCOM to the new value: {vcom_mV/1000}... ", end='')
                self.set_vcom(vcom_mV)
                print("Success" if self.get_vcom() == vcom_mV else "Failed")
    
    def _wait_ready(self):
        """
        The host must wait for the HRDY pin to be high before Tx/Rx of the next 
        2x8 bits.
        """
        while self._hrdy.value() == 0: pass

    def _send_command(self, command: Command):
        """
        Sends a command to the IT8951.
        Args:
            command: Command to execute
        """
        try:
            txdata = [SpiPreamble.COMMAND, command]
            self._wait_ready()
            self._ncs(0)
            for i in range(len(txdata)):
                self._wait_ready()
                self._spi.write(txdata[i].to_bytes(2, 'big'))
        finally:
            self._ncs(1)
    
    def _write_data(self, data: list):
        """
        Writes u16 words to the IT8951.
        Args: 
            data: A list of u16 elements containing the data to be written.
        """
        if not data: return
        try:
            txdata = [SpiPreamble.WRITE_DATA] + data
            self._wait_ready()
            self._ncs(0)
            for i in range(len(txdata)):
                self._wait_ready()
                self._spi.write(txdata[i].to_bytes(2, 'big'))
        finally:
            self._ncs(1)

    def _write_bytes(self, txbytes: bytearray):
        """
        This method should be used for non-register data transfers, where the 
        monitoring of the HRDY pin is irrelevant. Used to transfer images
        Args:
            txbytes: pre-formatted data bytes. Endianness depends on ImageInfo
        """
        if not txbytes: return
        try:
            self._wait_ready()
            self._ncs(0)
            self._spi.write(SpiPreamble.WRITE_DATA.to_bytes(2, 'big'))
            self._spi.write(txbytes)
        finally:
            self._ncs(1)

    def _send_command_args(self, command: Command, args: list):
        self._send_command(command)
        self._write_data(args)

    def _read_data(self, length: int) -> list:
        """
        Reads the specified number of 16bit words from the IT8951.
        Args:
            length: number of u16 elements to read.
        """
        if length == 0: return []

        try:
            # The first word returned from the controller is dummy:u16
            txdata = [SpiPreamble.READ_DATA] + [0]*(length+1)
            rxdata = []

            self._wait_ready()
            self._ncs(0)
            for i in range(len(txdata)):
                tx = txdata[i].to_bytes(2, 'big')
                self._wait_ready()
                rx = self._spi.read(1, tx[0]) + self._spi.read(1, tx[1])
                rxdata.append((rx[0] << 8) | rx[1])

            # Take off the first 2 words (preampble and dummy words)
            return rxdata[2:]
        finally:
            self._ncs(1)
            
    def _write_reg(self, reg: Register, data: int):
        """
        Writes the specified number of words to a register
        Args:
            reg: Register to write to
            data: u16 word to write to reg
        """
        self._send_command_args(Command.REG_WR, [reg, data])
    
    def _read_reg(self, reg: Register) -> int:
        """
        Reads the specified number of words from a register
        Args:
            reg: Register to write to
        """
        self._send_command_args(Command.REG_RD, [reg])
        return self._read_data(1)[0]

    def _wait_for_display_ready(self): 
        """
        Waits for the LUT engine to finish
        """
        while self._read_reg(Register.LUTAFSR) != 0: pass
    
    def set_i80_packed_mode(self, enable: bool):
        self._write_reg(Register.I80CPCR, int(enable))

    def sleep(self):
        self._send_command(Command.SLEEP)
        
    def standby(self):
        self._send_command(Command.STANDBY)
        
    def system_run(self):
        self._send_command(Command.SYS_RUN)
    
    def get_vcom(self) -> int:
        """
        Reads the VCOM value from the IT8951 in mV. Note that this should always
        be a negative value
        """
        self._send_command_args(Command.CMD_VCOM, [0])
        return -self._read_data(1)[0]

    def set_vcom(self, vcom_mV: int, store_to_flash: bool = False):
        """
        Sets the VCOM value on the IT8951.
        Args:
            vcom_mV: VCOM value in mV. Must be negative!
            store_to_flash: True stores the vcom_mV value in NVM. False by default
        """
        if vcom_mV >= 0: raise Exception("VCOM must be negative")
        arg = 2 if store_to_flash else 1
        # VCOM must be written as -1.58 = 1580 = 0x62C -> [0x06, 0x2C]
        self._send_command_args(Command.CMD_VCOM, [arg, abs(vcom_mV)])
    
    def set_power(self, enable: bool):
        self._send_command_args(Command.POWER_SEQUENCE, [enable])
        
    def get_device_info(self) -> DeviceInfo:
        self._send_command(Command.GET_DEV_INFO)
        rxdata = self._read_data(int(DeviceInfo.Size/2))
        return DeviceInfo.from_u16_words(rxdata)
    
    def fill_rect(self, rect: Rectangle, mode: DisplayMode, colour: int):
        """
        Fills the specified rectangle with a uniform color. The rectangle must
        be within the display's area and the pixel bit depth must not be more
        than 8bpp
        Args: 
            rect: Rectangle to colour uniformly
            colour: Colour to fill the rectangle with
        """
        if not rect.is_contained_within(self.panel_area):
            raise ValueError("Area outside the display's limits")
        if colour > 255:
            raise ValueError("Invalid colour for the max allowed pixel depth")
        # Refresh EPD and change image buffer content with the assigned colour
        arg4 = 0x1100 | mode 
        self._send_command_args(Command.FILL_RECT, rect.to_list() + [arg4, colour])
        
    def force_set_temperature(self, temperature_C: int):
        """
        Fixes the IT8951's temperature sensor readings to the specified 
        temperature in C
        """
        self._send_command_args(Command.CMD_TEMPERATURE, [1, temperature_C])

    def get_temperature(self) -> list:
        """
        Gets the real (0th) and forced (1st) temperature sensor reading from the
        IT8951. If the temperature value isn't fixed (forced), the 2nd touple 
        element is meaningless
        """
        self._send_command_args(Command.CMD_TEMPERATURE, [0])
        # TODO: The datasheet is ambiguous on the order of the real and forced T
        return self._read_data(2)
    
    def cancel_force_temperature(self):
        """
        After a forced (fixed) temperature settings this command ensures that
        the IT8951 continues to read the real temperature sensor.
        """
        self._send_command_args(Command.CMD_TEMPERATURE, [2])
    
    def set_bpp_mode(self, is_2bpp: bool):
        """
        This command was designed for 2 bpp image display. Without this command,
        2bpp cannot show correct white pixel. Host should call this command
        before display 2bpp image
        """
        self._send_command_args(Command.BPP_SETTINGS, [is_2bpp])

    def _load_img_area_start(self, img_info: ImageInfo, rect: Rectangle):
        self._send_command_args(Command.LD_IMG_AREA, \
                                [img_info.pack_to_u16()] + rect.to_list())

    def _load_img_end(self):
        self._send_command(Command.LD_IMG_END)

    def set_img_buff_base_address(self, base_address: int):
        if base_address & 0x3FF_FFFF != base_address:
            raise ValueError("Base address must be maximum 26 bits")

        addr_h = (base_address >> 16) & 0xFFFF
        addr_l = (base_address      ) & 0xFFFF
        self._write_reg(Register.LISAR,   addr_l)
        self._write_reg(Register.LISAR+2, addr_h)

    @classmethod
    def pack_pixels(cls, img_info: ImageInfo, rect: Rectangle, colour: list) -> list:
        # TODO: Generalise it to other bpps
        # The following alignment rules must be met:
        # 2bpp -> start_x % 8 = 0, end_x % 8 = 0
        # 4bpp -> start_x % 4 = 0, end_x % 4 = 0
        # 8bpp -> start_x % 2 = 0, end_x % 2 = 0
        pix_per_byte = ColorDepth.pixel_per_byte(img_info.bpp)

        words = []
        if img_info.bpp == ColorDepth.BPP_4BIT and img_info.endianness == Endianness.LITTLE:
            start_mod = rect.x % 4
            end_mod   = (rect.x + rect.width) % 4

            start_padding = start_mod if start_mod != 0 else 0
            end_padding   = 4 - end_mod if end_mod != 0 else 0

            # Loop backwards on the list to not mess up indices
            for row in range(rect.height-1, -1, -1):
                idx = (row+1)*rect.width
                colour[idx:idx] = [0]*end_padding
                idx = row*rect.width
                colour[idx:idx] = [0]*start_padding

        for i in range(0, len(colour), 4):
            words.append(colour[i] | (colour[i+1] << 4) | (colour[i+2] << 8) | (colour[i+3] << 12))
        return words

    def write_packed_pixels(self, img_info: ImageInfo, rect: Rectangle, data):
        """
        Writes the specified pixels to the IT8951's internal frame buffer but
        does not render the image on the screen. Call display_area after writing
        the pixels to display on the EPD
        Args:
            rect: Rectangle to colour with the specified pixels. The area of the
                  rectangle must match the number of pixels in the colour list
            colour: List of pixels to write to the area defined by 'rect'.
        """
        if img_info.bpp == ColorDepth.BPP_1BIT: 
            raise NotImplementedError("The feature is not supported")
        if not rect.is_contained_within(self.panel_area):
            raise ValueError("Area outside the display's limits")

        self._load_img_area_start(img_info, rect)
        if isinstance(data, list):
            self._write_data(data)
        elif isinstance(data, bytearray):
            self._write_bytes(data)
        else:
            raise TypeError("data argument must be a list or a bytearray")
        self._load_img_end()

    def load_bmp(self, x: int, y: int, img: str):
        with open(img, 'rb') as f:
            # Handle lazyness. See https://en.wikipedia.org/wiki/BMP_file_format)
            if f.read(2) != b'BM':
                raise ValueError("BMP must have Windows (BM) bitmap header")

            # byte [10:13] encodes the pixel byte array offset in the img
            f.seek(10) 
            pix_arr_offset = int.from_bytes(f.read(4), 'little')

            # byte [18:21] encodes the bitmap width in pixels
            # byte [22:25] encodes the bitmap height in pixels
            f.seek(18) 
            width = int.from_bytes(f.read(4), 'little')
            height = int.from_bytes(f.read(4), 'little')

            # byte [28:29] encodes the bpp of the image
            f.seek(28)
            bpp = int.from_bytes(f.read(2), 'little')

            buf = bytearray(int(width*height/(8/bpp)))

            f.seek(pix_arr_offset)
            f.readinto(buf)

        rect = Rectangle(x, y, width, height)
        img_info = ImageInfo(Endianness.LITTLE, ColorDepth.bpp_to_code(bpp), RotateMode.ROTATE_0)
        self.write_packed_pixels(img_info, rect, buf)

    def display_area(self, rect: Rectangle, display_mode: DisplayMode):
        """
        Displays the pixels loaded to the frame buffer to the specified area
        """
        self._wait_for_display_ready()
        self._send_command_args(Command.DPY_AREA, rect.to_list() + [display_mode])
