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


