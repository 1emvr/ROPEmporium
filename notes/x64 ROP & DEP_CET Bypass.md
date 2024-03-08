ROP Basics: [Exploit writing tutorial part 10 : Chaining DEP with ROP – the Rubik’s[TM] Cube](https://www.corelan.be/index.php/2010/06/16/exploit-writing-tutorial-part-10-chaining-dep-with-rop-the-rubikstm-cube/) 🙀
# Basics
## Setting boot-time NX option
```
bcdedit.exe /v -- show all
bcdedit.exe /set nx OptIn
bcdedit.exe /set nx OptOut
bcdedit.exe /set nx AlwaysOn
bcdedit.exe /set nx AlwaysOff
```

Loaded module/ main executable gadgets will be the only way to execute instructions, using data on the stack as parameters. Specific settings will require a specific approach and technique.

Existing module functions will provide the following:
- execute commands (e.g. WinExec)
- Mark the page that contains shellcode as executable and jump
- copy data into executable regions and jump
- change DEP settings for the current process

Bypassing or changing DEP settings can all be done with native Windows API calls 

#### Overcoming ASLR
- cause a memory leak to a module/ library
- take brute-force approach (unreasonable on 64-bit systems)
- choose a module that doesn't have ASLR/Rebase enabled

## Useful Gadgets
https://trustfoundry.net/2019/07/18/basic-rop-techniques-and-tricks/

`pop rxx; ret` - popping a value from the stack into registers and ret
`push esp; ret` - pushes stack pointer onto the stack and ret
`xchg rxx, esp; ret` - exchange stack pointer with specified register and ret
`add ebx, 0x12345678; ret` - add a constant value to register and ret

- When you don't have the gadgets you want, you can still use `xor` and `xchg` gadgets to perform some juggling.
- Xoring registers against themselves sums 0, of course... xoring an empty register against a non-empty register will duplicate it's value (`math stuff`).
- Xchg obviously exchanges 2 registers values

#### Stack Alignment
If a system function call crashes somewhere on a `movaps` instruction or `do_system()` it could indicate that the payload is not 16-byte aligned. Easy fix is to find an `extra ret instruction` and adding it before the call to get correct alignment
#### Imports
If a random function imports a useful library function, you don't need to call that random funciton in order to use the library function 

Ex:
```
...junk (top to bottom/reversed)
rop gadgets
ESP-> SSN or fnPtr
param
param
param
param
...
nops
shellcode
more data

---- General control flow (simple) ----
high memory address
&exit() <-- rop3 return address
&rop3() <-- rop2 return address
&rop2() <-- rop1 return address
&rop1() <-- Vulnerable return address
RBP     <-- Can be 4 non-null bytes
AAAA
AAAA
AAAA
AAAA
AAAA
low memory address
```

## Stack Pivots
[Exploitation - Binary Exploitation (gitbook.io)](https://ir0nstone.gitbook.io/notes/types/stack/stack-pivoting/exploitation)
#### Gadgets
- pop rsp gadget - `pop rsp; ret`
- xchg gadget - `pop rxx; value; xchg rxx, rsp`
- leave gadget - `leave; ret` or `mov rsp, rbp; pop rbp`
## Write What Where
### Heap Overflow (malloc/free)
Metadata for memory allocation might be overwritten in some way
```cpp
#define BUFLEN 256
int main(int argc, char **argv) {
	char* buf1 = (char*) malloc(BUFLEN);
	char* buf2 = (char*) malloc(BUFLEN);

	strcpy(buf1, argv[1]);
	free(buf2);
}
```

- `_strcpy` can be used to overwrite the end of `buf1` into `buf2`
- The C-standard uses a linked-list structure to track allocation/deallocation
- Call to `_free` should use data from `buf2` in order to re-write the linked list:
	- the `next*` pointer for `buf1` will be updated as `prev*` for any subsequent ptr respectively
	- adding arbitrary memory to `next*` inside `buf2` should allow an update of `buf1` link once the second block is freed.

### Format String
#### Example 1 - Addresses 
These are extremely rare in today's development.
```cpp
int main() {
	char name[64] = { 0 };
	read(stdin, name, 64);
	printf(name);
	return 0;
}
```

- print format modifiers `%x.%x.%x.%x.` to pop values off the stack\[4\]
- `_printf` can index to an arbitrary array within arguments: `%n$x`

```cpp
'BBBBBBBB' %p.%p.%p.%p. -> 
	"0x7ffffdc3646cbcc 0x3733d332cdbc 0x4242424242424242 07fffff..."
```
Input on the stack is at the 3rd position. Using different format specifiers @ our input's position to observe the behavior

```cpp
'BBBBBBBB' %p.%p.%s.%p. -> 
	Segmentation fault(core dumped)
```
A crash indicates this would be deferenced as address `0x4242424242424242` which is not valid.  This is trying to dereference as a pointer.

#### Example 2 - Hidden Data
```cpp
char data[] = "comd get me\n";
int main(int argc, char **argv) {

	printf("Hidden data at %p\n", &data);
	char buffer[32];
	get(buffer);

	printf(buffer);
	printf("\n");
}

AAAA %11$p %p %p %p %p %p %p %p %p ->
	0x41414141 0x5568933d 0x9e 0x3347eefd (nil) 0xf7773def ...
```
### Use After Free
### Integer Overflow
### Pointer Subterfuge

# Windows Specific
## Function params and usage

#### Custom Gadgets
> Note - Setting certain values on the stack or registers can alter other values/registers

Some examples of functions that can be manipulated to disable/bypass DEP:
- __VirtualAlloc + memcpy:__
	Creation executable pages, copy shellcode and execute. A 2-chain may be required.
- __HeapCreate(HEAP_CREATE_ENABLE_EXECUTE) + HeapAlloc:__
	Provides the same, but a 3-chain may be required.
- __SetProcessDEPPolicy :__
	Allowing to directly change the DEP policy for current process
- __NtSetInformationProcess :__                                         
	Changes the DEP policy as well
- __VirtualProtect :__
	Changes access protection level of a page
- __WriteProcessMemory :__
	Copies code to another process

Obviously, setting up the stack changes with each API for their arguments. In order to do this, the ESP/RSP must point to the API functions parameters. Most of the time will be returning back to the stack.

First, pointer to VirtualAlloc() must be at the top of the stack, which is then followed by the following parameters:

### VirtualAlloc
```
rsp -> ....
DWORD_PTR [kernel32.VirtualAlloc]
```

```
- rax : pointer to __memcpy() (return address for VirtualAlloc, once it's done)
- rcx : lpAddress (arbitrary address, e.g. 0x00200000). Can probably be anywhere
- rdx : size of shellcode++
- r8 : flAllocationType (MEM_COMMIT)
- r9 : flProtect (PAGE_EXECUTE_READWRITE)

ret __memcpy()
```

### \_\_memcpy():
```
DWORD_PTR [ucrt.memcpy]
```

```
- rcx : lpAddress            (__memcpy( &dst , ... , ... ))
- rdx : Address of shellcode (__memcpy( ... , &src , ... ))
- r8 : Size                  (__memcpy( ... , ... , size ))

jmp lpAddress
```

### WriteProcessMemory Injection
```
rsp -> ...
DWORD_PTR [kernel32.WriteProcessMemory]
```

```
rax : return address                                    (0x77121010)
rcx : hProcess (-1) or such                             (0xFFFFFFFF)
rdx : lpBaseAddress (region for shcode/module patching) (0x77121010)
r8 : lpBuffer (shellcode ptr)                           (to be continued...)
r9 : nSize                                              (to be continued...)
lpNumberOfBytesWritten                                  (0x77121004)
```

Notice that `lpNumberOfBytesWritten` address is before the destination address, to prevent it from possibly overwriting the shellcode.
#### WPM Technique 1: Full WPM()
Simply write shellcode to executable memory and jump. Patching is possible with this. Be cautious of what you overwrite as the overwritten code could be used by your implant, therefore, corrupting it.

Another problem is that once the region is written, executable write-permissions will be downgraded again once the call is finished. If you have encoded/encrypted shellcode, it will not be permitted to modify itself `(no sleep-obf, decryption, spoofing or otherwise)`. This can be an issue because of bad characters. 

Prepending the shellcode with another calling `VirtualProtect()` is a possible fix but might be better suited for patching purposes.

#### WPM Technique 2: Patching WPM()
Writing yourself directly into kernel32 is possible, overtop the `WriteProcessMemory` function. A problem with this is a size restriction.

Within WPM, a number of calls and jmps are made by the function to copy shellcode from the stack to destination:
```
0x7C802222: Call ntdll.ZwProtectVirtualMemory
0x7C802271: Call ntdll.ZwWriteVirtualMemory
0x7C80228B: Call ntdll.ZwFlushInstructionCache
0x7C8022C9: Call ntdll.ZwWriteVirtualMemory(again)
```
Once this is finished, WPM will copy the shellcode into the region and will write back to `lpNumberOfBytesWritten` and return. This final routine starts at `0x7C8022CF`.  

Overwriting this area would black-hole to our shellcode upon subsequent instructions. `(investigate this)`. `0x7C8022CF` would be good address to use as the destination.

`lpNumberOfBytesWritten` still needs to point to writable memory. The first parameter (`return address`) would no longer matter in this case. Reminder that the destination address needs to remain within the bounds of `WriteProcessMemory`. Writing too far into kernel32 could corrupt memory.
```
rax : return address               (0xFFFFFFFF)
rcx : hProcess                     (0xFFFFFFFF or otherwise)
rdx : lpBaseAddress                (0x7C8022CF)
r8 : lpBuffer                      (to be continued...)
r9 : nSize                         (to be continued...)
lpNumberOfBytesWritten             (any writable location)
```

When beginning to build ROP exploits, likely will end up hard coding function pointer addresses. (`try to get function ptr`)

#### Possible vector for remote injection
```
WPM_T _WriteProcessMemory = GetProcAddress(GetModuleHandle("ntdll"),"WriteProcessMemory")

???
```

