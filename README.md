# i2c-tools
Python tooling for interacting with i2c devices using an FTDI FT232H chip.
## Install requirements
<code>pip install -r requirements.txt</code>

## Examples
Read from address: 
<code>python i2c_tools.py --eeprom_device atmel_24c256 0x50 mode read_from</code><br/>
Write to address: 
<code>python i2c_tools.py --eeprom_device atmel_24c256 0x50 mode write_to</code><br/>
Dump full chip content: <code>python i2c_tools.py -o mem.out --eeprom_device atmel_24c256 0x50 mode dump_full_content</code>

## Support
Tested devices: atmel_24c256, st_m24215_w, st_m24128_bw.
