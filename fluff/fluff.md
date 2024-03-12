#### pwnme
```asm
public pwnme
pwnme proc near

s= byte ptr -20h
...
lea     rdi, aYouKnowChangin ; "You know changing these strings means I"...
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
...
```

#### print_file
```asm
...
mov     [rbp+filename], rdi
mov     [rbp+stream], 0
mov     rax, [rbp+filename]
lea     rsi, modes      ; "r"
mov     rdi, rax        ; filename
call    _fopen
...
```

```
You know changing these strings means I have to rewrite my solutions...
>
```
