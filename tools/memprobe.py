"""Dev tool: read native code behind UFunctions in the running game (read-only).

    python tools/memprobe.py <UE4SS.log>
Reads "[PROBE] <path> 0x<address>" lines, finds each UFunction's native function pointer (the 8-byte
value inside the UFunction object that points into the game exe's code), and dumps the code bytes.
"""
import ctypes
import ctypes.wintypes as wt
import re
import struct
import subprocess
import sys

k32 = ctypes.WinDLL("kernel32", use_last_error=True)
psapi = ctypes.WinDLL("psapi")
k32.OpenProcess.restype = wt.HANDLE
k32.ReadProcessMemory.argtypes = [wt.HANDLE, ctypes.c_void_p, ctypes.c_void_p, ctypes.c_size_t,
                                  ctypes.POINTER(ctypes.c_size_t)]


def pid_of(exe="Dungeons-Win64-Shipping.exe"):
    out = subprocess.run(["tasklist", "/FI", f"IMAGENAME eq {exe}", "/FO", "CSV", "/NH"],
                         capture_output=True, text=True).stdout
    for line in out.splitlines():
        p = [x.strip('"') for x in line.split('","')]
        if p and p[0].lower() == exe.lower():
            return int(p[1])


def alive(h):
    """True while the process behind this handle runs. Instant, unlike pid_of (which starts tasklist, 0.2 s)."""
    code = wt.DWORD()
    return bool(k32.GetExitCodeProcess(wt.HANDLE(h), ctypes.byref(code))) and code.value == 259   # STILL_ACTIVE


def read(h, addr, n):
    buf = ctypes.create_string_buffer(n)
    got = ctypes.c_size_t()
    if not k32.ReadProcessMemory(h, ctypes.c_void_p(addr), buf, n, ctypes.byref(got)):
        return None
    return buf.raw[:got.value]


def main_module(h):
    mods = (wt.HMODULE * 1024)()
    need = wt.DWORD()
    psapi.EnumProcessModulesEx(h, ctypes.byref(mods), ctypes.sizeof(mods), ctypes.byref(need), 3)
    base = mods[0]
    hdr = read(h, base, 0x1000)
    pe = struct.unpack_from("<I", hdr, 0x3C)[0]
    size = struct.unpack_from("<I", hdr, pe + 24 + 56)[0]
    return base, size


if __name__ == "__main__":
    log = open(sys.argv[1], encoding="utf-8", errors="ignore").read()
    probes = re.findall(r"\[PROBE\] (\S+) 0x([0-9A-F]+)", log)
    h = k32.OpenProcess(0x0410, False, pid_of())  # QUERY_INFORMATION | VM_READ
    base, size = main_module(h)
    print(f"exe base 0x{base:X} size 0x{size:X}")
    for path, addr in probes:
        a = int(addr, 16)
        obj = read(h, a, 0x100)
        cands = [(off, struct.unpack_from("<Q", obj, off)[0]) for off in range(0, 0x100, 8)]
        code_ptrs = [(off, v) for off, v in cands if base <= v < base + size]
        print(f"\n{path}")
        for off, v in code_ptrs:
            if off != 0xC0:  # UFunction::Func (native thunk)
                continue
            code = read(h, v, 64) or b""
            print(f"  thunk exe+0x{v - base:X}")
            for i in range(len(code) - 5):  # follow every direct call in the thunk
                if code[i] == 0xE8:
                    tgt = v + i + 5 + struct.unpack_from("<i", code, i + 1)[0]
                    if base <= tgt < base + size:
                        body = read(h, tgt, 96) or b""
                        print(f"    call -> exe+0x{tgt - base:X}: {body.hex(' ')}")
