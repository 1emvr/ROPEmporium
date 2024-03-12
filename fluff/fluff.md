# Fluff

```
[lemur@archlinux](fluff)$ checksec --file=fluff
RELRO           STACK CANARY      NX            PIE             RPATH      RUNPATH      Symbols         FORTIFY Fortified       Fortifiable     FILE
Partial RELRO   No canary found   NX enabled    No PIE          No RPATH   RW-RUNPATH   65 Symbols        No    0               0               fluff
```

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

#### Sections
```sh
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


[lemur@archlinux](fluff)$ objdump -s -j .data fluff

fluff:     file format elf64-x86-64

Contents of section .data:
 601028 00000000 00000000 00000000 00000000  ................

Contents of section .bss:
 601038 00000000 00000000                    ........

```
