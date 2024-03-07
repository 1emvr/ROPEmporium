```
pwnme proc near

s= byte ptr -20h

; __unwind {
push    rbp
mov     rbp, rsp
sub     rsp, 20h
lea     rax, [rbp+s]
mov     edx, 20h ; ' '  ; n
mov     esi, 0          ; c
mov     rdi, rax        ; s
call    _memset
mov     edi, offset aHopeYouReadThe ; "Hope you read the instructions...\n"
call    _puts
mov     edi, offset format ; "> "
mov     eax, 0
call    _printf
lea     rax, [rbp+s]
mov     edx, 200h       ; nbytes
mov     rsi, rax        ; buf
mov     edi, 0          ; fd
call    _read
mov     edi, offset aThankYou ; "Thank you!"
call    _puts
nop
leave
retn
; } // starts at 400898
pwnme endp

usefulFunction proc near
; __unwind {
push    rbp
mov     rbp, rsp
mov     edx, 6
mov     esi, 5
mov     edi, 4
call    _callme_three
mov     edx, 6
mov     esi, 5
mov     edi, 4
call    _callme_two
mov     edx, 6
mov     esi, 5
mov     edi, 4
call    _callme_one
mov     edi, 1          ; status
call    _exit
; } // starts at 4008F2
usefulFunction endp
```

- 32 byte buffer `s`
- call `_read` up to 512 bytes

- `0x00000000004008f2  usefulFunction`
- `0x0000000000400720  callme_one@plt`
- `0x00007ffff7c0081a  callme_one`
- `0x0000000000400740  callme_two@plt`
- `0x00007ffff7c0092b  callme_two`
- `i0x00000000004006f0  callme_three@plt`
- `0x00007ffff7c00a2d  callme_three`

each callme function takes 3 arguments, edi,esi,edx

 
