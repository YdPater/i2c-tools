# i2c-tools
Python tooling for interacting with i2c devices using an FTDI FT232H chip. Made this to learn about how the i2c protocol works. 

## Install requirements
<code>pip install -r requirements.txt</code>

## Examples
Read from address: 
<code>python i2c_tools.py --eeprom_device atmel_24c256 0x50 mode read_from</code><br/>
Write to address: 
<code>python i2c_tools.py --eeprom_device atmel_24c256 0x50 mode write_to</code><br/>
Dump full chip content: <code>python i2c_tools.py -o mem.out --eeprom_device atmel_24c256 0x50 mode dump_full_content</code>

## Support
Only tested on the Atmel 24c256. Bigger or smaller versions of this chip should also work when the chip size is changed.
