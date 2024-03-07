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

```
