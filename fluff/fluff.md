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

#### mov gadgets
```asm
[INFO] File: fluff
0x00000000004005e2: mov byte ptr [rip + 0x200a4f], 1; pop rbp; ret;
0x0000000000400606: mov dword ptr [rbp + 0x48], edx; mov ebp, esp; call 0x500; mov eax, 0; pop rbp; ret;
0x0000000000400610: mov eax, 0; pop rbp; ret;
0x00000000004004d5: mov eax, dword ptr [rip + 0x200b1d]; test rax, rax; je 0x4e2; call rax;
0x00000000004004d5: mov eax, dword ptr [rip + 0x200b1d]; test rax, rax; je 0x4e2; call rax; add rsp, 8; ret;
0x0000000000400609: mov ebp, esp; call 0x500; mov eax, 0; pop rbp; ret;
0x00000000004005db: mov ebp, esp; call 0x560; mov byte ptr [rip + 0x200a4f], 1; pop rbp; ret;
0x0000000000400619: mov ebp, esp; mov edi, 0x4006c4; call 0x510; nop; pop rbp; ret;
0x000000000040061b: mov edi, 0x4006c4; call 0x510; nop; pop rbp; ret;
0x000000000040057c: mov edi, 0x601038; jmp rax;
0x00000000004004d4: mov rax, qword ptr [rip + 0x200b1d]; test rax, rax; je 0x4e2; call rax;
0x00000000004004d4: mov rax, qword ptr [rip + 0x200b1d]; test rax, rax; je 0x4e2; call rax; add rsp, 8; ret;
0x0000000000400608: mov rbp, rsp; call 0x500; mov eax, 0; pop rbp; ret;
0x00000000004005da: mov rbp, rsp; call 0x560; mov byte ptr [rip + 0x200a4f], 1; pop rbp; ret;
0x0000000000400618: mov rbp, rsp; mov edi, 0x4006c4; call 0x510; nop; pop rbp; ret;
```

#### pop gadgets
```asm
[INFO] File: fluff
0x000000000040069c: pop r12; pop r13; pop r14; pop r15; ret;
0x000000000040069e: pop r13; pop r14; pop r15; ret;
0x00000000004006a0: pop r14; pop r15; ret;
0x00000000004006a2: pop r15; ret;
0x000000000040057b: pop rbp; mov edi, 0x601038; jmp rax;
0x000000000040069b: pop rbp; pop r12; pop r13; pop r14; pop r15; ret;
0x000000000040069f: pop rbp; pop r14; pop r15; ret;
0x0000000000400588: pop rbp; ret;
0x000000000040062b: pop rcx; add rcx, 0x3ef2; bextr rbx, rcx, rdx; ret;
0x00000000004006a3: pop rdi; ret;
0x000000000040062a: pop rdx; pop rcx; add rcx, 0x3ef2; bextr rbx, rcx, rdx; ret;
0x00000000004006a1: pop rsi; pop r15; ret;
0x000000000040069d: pop rsp; pop r13; pop r14; pop r15; ret;
```

#### call gadgets
```asm
0x000000000040060b: call 0x500; mov eax, 0; pop rbp; ret;
0x0000000000400620: call 0x510; nop; pop rbp; ret;
0x00000000004005dd: call 0x560; mov byte ptr [rip + 0x200a4f], 1; pop rbp; ret;
0x000000000040070f: call qword ptr [rax + 1];
0x00000000004007a3: call qword ptr [rax];
0x00000000004007c3: call qword ptr [rcx];
0x00000000004004e0: call rax;
0x00000000004004e0: call rax; add rsp, 8; ret;
```

Looking through ida, there was one function that was not present in the table. Using `objdump` i was able to find it:
```asm
0000000000400628 <questionableGadgets>:
  400628:       d7                      xlat   %ds:(%rbx)
  400629:       c3                      ret
  40062a:       5a                      pop    %rdx
  40062b:       59                      pop    %rcx
  40062c:       48 81 c1 f2 3e 00 00    add    $0x3ef2,%rcx
  400633:       c4 e2 e8 f7 d9          bextr  %rdx,%rcx,%rbx
  400638:       c3                      ret
  400639:       aa                      stos   %al,%es:(%rdi)
  40063a:       c3                      ret
  40063b:       0f 1f 44 00 00          nopl   0x0(%rax,%rax,1)
```

- `xlat/xlatb` (table lookup translation) - Replaces the byte in AL with byte from a user table addressed by BX. Essentially, allows to read from the `.data` segment
```asm
section .data
	table db 0x10,0x20,0x30,0x40,0x50

section .text
	global _start

_start:
	mov	al, 2 	;; initial value
	mov	bl, 1
	mov 	dl, [table]
	xlat

	al = 0x20
```

- `bextr` (bitfield extract) - Shifts desired bit field position down to LSB in AL
```asm
section .data
	operand dq 0x1234567890ABCDEF

section .text
	global _start

_start:
	mov 	rax, [operand]
	mov	rcx, 4
	mov 	rdx, 4
	bextr	rax, rax, rcx, rdx

	AL = 5678
```

- `stos` stores a byte, word or dword from AL, AX or EAX regsiter into dst from ES:EDI or ES:DI
```asm
section .data
	buffer db 10 dup(?)

section .text
	global _start

_start:
	mov 	ecx, 10 	;; set loop counter to 10
	mov 	edi, buffer	;; set dst index to start of buffer
	mov	al, 'A'		;; set AL register to the desired value to store

store_loop:
	stosb 			;; store AL to the buffer
	inc	edi		;; increment the index
	loop 	store_loop	;; repeat until 0
```
