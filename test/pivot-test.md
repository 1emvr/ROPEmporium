```asm
vuln
vuln proc near

s= byte ptr -70h
var_8= qword ptr -8

; __unwind {
push    rbp
mov     rbp, rsp
sub     rsp, 70h
mov     rax, fs:28h
mov     [rbp+var_8], rax
xor     eax, eax
lea     rax, [rbp+s]
mov     rsi, rax
lea     rax, format     ; "Try pivoting to: %p\n"
mov     rdi, rax        ; format
mov     eax, 0
call    _printf
mov     rdx, cs:__bss_start ; stream
lea     rax, [rbp+s]
mov     esi, 80h        ; n
mov     rdi, rax        ; s
call    _fgets
nop
mov     rax, [rbp+var_8]
sub     rax, fs:28h
jz      short locret_4011F7``


 Attributes: bp-based frame

public winner
winner proc near

var_8= dword ptr -8
var_4= dword ptr -4

; __unwind {
push    rbp
mov     rbp, rsp
sub     rsp, 10h
mov     [rbp+var_4], edi
mov     [rbp+var_8], esi
cmp     [rbp+var_4], 0DEADBEEFh
jnz     short loc_401187

...
cmp     [rbp+var_8], 0DEADC0DEh
jnz     short loc_401187
```

- winner @ 0x0000000000401156
