"""Dev tool: patch bytes in the running game's code (memory only; gone when the game closes).

    python tools/mempatch.py <exe_offset_hex> <expected_hex> <new_hex> [...more triples]
Each patch is checked against the expected original bytes first.
"""
import ctypes
import ctypes.wintypes as wt
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from memprobe import main_module, pid_of, read  # noqa: E402

k32 = ctypes.WinDLL("kernel32", use_last_error=True)
k32.OpenProcess.restype = wt.HANDLE
k32.VirtualProtectEx.argtypes = [wt.HANDLE, ctypes.c_void_p, ctypes.c_size_t, wt.DWORD, ctypes.POINTER(wt.DWORD)]
k32.WriteProcessMemory.argtypes = [wt.HANDLE, ctypes.c_void_p, ctypes.c_void_p, ctypes.c_size_t,
                                   ctypes.POINTER(ctypes.c_size_t)]
k32.FlushInstructionCache.argtypes = [wt.HANDLE, ctypes.c_void_p, ctypes.c_size_t]


def write(h, base, offset, old, new):
    """Replace `old` with `new` at exe+offset; refuses if the current bytes aren't `old`."""
    addr = base + offset
    cur = read(h, addr, len(old))
    if cur == new:
        print(f"exe+0x{offset:X}: already patched")
        return
    if cur != old:
        sys.exit(f"exe+0x{offset:X}: expected {old.hex(' ')}, found {cur.hex(' ') if cur else None} - not patching")
    prot = wt.DWORD()
    k32.VirtualProtectEx(h, ctypes.c_void_p(addr), len(new), 0x40, ctypes.byref(prot))
    k32.WriteProcessMemory(h, ctypes.c_void_p(addr), new, len(new), None)
    k32.VirtualProtectEx(h, ctypes.c_void_p(addr), len(new), prot.value, ctypes.byref(prot))
    k32.FlushInstructionCache(h, ctypes.c_void_p(addr), len(new))
    print(f"exe+0x{offset:X}: {old.hex(' ')} -> {read(h, addr, len(new)).hex(' ')}")


if __name__ == "__main__":
    h = k32.OpenProcess(0x0438, False, pid_of())  # VM_OPERATION | VM_READ | VM_WRITE | QUERY_INFORMATION
    base, _ = main_module(h)
    args = sys.argv[1:]
    for i in range(0, len(args), 3):
        write(h, base, int(args[i], 16), bytes.fromhex(args[i + 1]), bytes.fromhex(args[i + 2]))
