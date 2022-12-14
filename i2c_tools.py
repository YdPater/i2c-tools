from pyftdi.i2c import I2cController, I2cNackError
from argparse import ArgumentParser
from sys import exit
from math import floor


class Handler:
    def __init__(self, eeprom_addr: int, i2c: I2cController) -> None:
        self._eeprom_addr = eeprom_addr
        self._i2c = i2c
        self.slave = self._i2c.get_port(self._eeprom_addr)
    
    @property
    def eeprom_addr(self) -> hex:
        return self._eeprom_addr
    
    @property
    def i2c(self) -> I2cController:
        return self._i2c
    
    @eeprom_addr.setter
    def eeprom_addr(self, eeprom_addr: int) -> None:
        if not isinstance(eeprom_addr, int):
            raise ValueError("i2c_addr must be of type int")
        self._eeprom_addr = eeprom_addr
    
    @i2c.setter
    def i2c(self, i2c: I2cController) -> None:
        if not isinstance(i2c, I2cController):
            raise ValueError("i2c must be of type I2cController")
        self._i2c = i2c

    def read_from_2byte_cell_addr(self, cel_addr_1: int,
                                cel_addr_2: int, readlen: int) -> hex:
        data = self.slave.exchange([cel_addr_1, cel_addr_2], readlen)
        return data
    
    def write_to_addr(self, addr_1: int, addr_2, value: hex) -> None:
        if not isinstance(addr_1, int) or not isinstance(addr_2, int):
            raise ValueError("Address parts must be in int format")
        self.slave.write([addr_1, addr_2, value], relax=True, start=True)
        self.slave.write([], relax=True, start=False)
         
    def dump_head(self) -> None:
        num_of_reads = 100
        _data = self.read_from_2byte_cell_addr(0x00, 0x00, num_of_reads)
        _addr = 0
        amount_per_row = 20
        counter = 0
        for d in _data:
            if counter == 0:
                print(f"{_addr:#0{6}x}| ", end="")
            if counter < amount_per_row -1:
                print(f"{d:#0{4}x}", end=" ")
                counter += 1
                _addr += 1
            else:
                print(f"{d:#0{4}x}")
                counter = 0
                _addr += 1
        print()
    
    def dump_full_content(self, outputfile: str):
        chunk_size = 256
        counter = 0
        high, _ = divmod(self.device_size, 0x100)
        with open(outputfile, "ab") as outfile:
            while True:
                data = self.read_from_2byte_cell_addr(counter, 0x00, chunk_size)
                counter += 1
                outfile.write(bytes(data))
                if counter == high + 1:
                    return
            


class Atmel_24c256(Handler):
    company = "Atmel"
    device_type = "24c256"
    device_size = 0x7fff
    
    def __init__(self, eeprom_addr: int, i2c: I2cController) -> None:
        super().__init__(eeprom_addr, i2c)


class ST_M24215_W(Handler):
    company = "STM"
    device_type = "m24215-w"
    device_size = 0xffff
    
    def __init__(self, eeprom_addr: int, i2c: I2cController) -> None:
        super().__init__(eeprom_addr, i2c)


class ST_M24128_BW(Handler):
    company = "STM"
    device_type = "m24128bw"
    device_size = 0x3e80

    def __init__(self, eeprom_addr: int, i2c: I2cController) -> None:
        super().__init__(eeprom_addr, i2c)
    
    def dump_full_content(self, outputfile: str):
        chunk_size = 256
        counter = 0
        with open(outputfile, "ab") as outfile:
            while True:
                if counter == 0x3e:
                    data = self.read_from_2byte_cell_addr(counter, 0x00, 0x80)
                    outfile.write(bytes(data))
                    return 
                else:   
                    data = self.read_from_2byte_cell_addr(counter, 0x00, chunk_size)
                    counter += 1
                    outfile.write(bytes(data))


def main(chip, args):
    if args.mode == "dump_head":
        chip.dump_head()
    elif args.mode == "dump_full_content":
        chip.dump_full_content(args.output_file)
    elif args.mode == "write_to" or args.mode == "read_from":
        addr = input("Supply the 4 byte address to write to (ex: 0x0001): ")
        if len(addr) < 6 or addr[1] != "x":
            print("[!] Please submit the entire 4 byte HEX string with leading zeroes (eg 0x0001)")
            exit()
        addr_1 = addr[:4]
        addr_2 = "0x" + addr[4:]
        
        try:
            addr_1 = int(addr_1, 16)
            addr_2 = int(addr_2, 16)
        except ValueError: 
            print("Please supply a valid HEX address.")
            exit()
        
        if args.mode == "write_to":
            str_value = input("Please supply the HEX value to write to the register (ex: 0x41): ")
            try:
                value = int(str_value, 16)
            except ValueError:
                print("[!] Supply a valid HEX byte to write.")
                exit()
            while True:
                choice = input(f"I am about to write {str_value} to register {addr}, confirm (Y/n): ")
                if choice == "Y":
                    break
                elif choice == "n":
                    print("[!] Verification failed, exiting.")
                    exit()
                
            try:
                chip.write_to_addr(addr_1, addr_2, value)
                print(f"Byte successfully written to: {addr}. Data currently in register: {hex(chip.read_from_2byte_cell_addr(addr_1, addr_2, 1))}")
            except I2cNackError:
                print("[!] Received NACK message from device. Write failed!")
                exit()
        else:
            try:
                ans = chip.read_from_2byte_cell_addr(addr_1, addr_2, 1)[0]
                print(f"HEX value found at {addr} -> {hex(ans)}")
            except I2cNackError:
                print("[!] Received NACK message from device. Write failed!")
                exit()



if __name__ == "__main__":
    parser = ArgumentParser(
        description=
        "I2C EEPROM toolkit for ftdi chipsets. (ATMEL 24c256 is supported)")
    parser.add_argument("EEPROM_ADDR",
                        help="Specify the EEPROM slave address.",
                        type=str, default=0x50)
    parser.add_argument("--ftdi_device",
                        help="Specify the FTDI device to use. Default: 'ftdi://:/1'",
                        type=str, default="ftdi://:/1")
    parser.add_argument("--eeprom_device", choices=["atmel_24c256", "st_m24215_w", "st_m24128bw"], required=True)
    parser.add_argument("-o" , "--output-file", help="Specify dump file for eeprom contents", default="mem.out")
    subparsers = parser.add_subparsers(dest="Mode command")
    subparsers.required = True
    mode_parser = subparsers.add_parser("mode")
    mode_parser.add_argument("mode", choices=['dump_head', 'dump_full_content','read_from', "write_to"], help="Select the desired operation")

    args = parser.parse_args()

    eeprom_addr = int(args.EEPROM_ADDR, 16)

    i2c = I2cController()
    i2c.configure(args.ftdi_device)

    if args.eeprom_device == "atmel_24c256":
        chip = Atmel_24c256(eeprom_addr, i2c)
    elif args.eeprom_device == "st_m24215_w":
        chip = ST_M24215_W(eeprom_addr, i2c)
    elif args.eeprom_device == "st_m24128bw":
        chip = ST_M24128_BW(eeprom_addr, i2c)
    else:
        print("[!] Unsupported chip. See help for available devices.")
    main(chip, args)
    
