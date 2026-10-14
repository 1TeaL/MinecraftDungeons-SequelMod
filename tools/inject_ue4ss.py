"""Load UE4SS into an already-running Minecraft Dungeons.

The Steam exe is packed: its code is encrypted on disk and unpacked at startup, so UE4SS crashes
if it loads with the game (dwmapi.dll proxy). Loading it once the game has reached the menu works
around that.

    python tools/inject_ue4ss.py          # wait for the game, then load UE4SS
"""
import ctypes
import ctypes.wintypes as wt
import subprocess
import sys
import time
from pathlib import Path

GAME = Path(__file__).resolve().parents[3]
DLL = GAME / "Dungeons" / "Binaries" / "Win64" / "ue4ss" / "UE4SS.dll"
EXE = "Dungeons-Win64-Shipping.exe"

k32 = ctypes.WinDLL("kernel32", use_last_error=True)
k32.OpenProcess.restype = wt.HANDLE
k32.VirtualAllocEx.restype = ctypes.c_void_p
k32.VirtualAllocEx.argtypes = [wt.HANDLE, ctypes.c_void_p, ctypes.c_size_t, wt.DWORD, wt.DWORD]
k32.WriteProcessMemory.argtypes = [wt.HANDLE, ctypes.c_void_p, ctypes.c_void_p, ctypes.c_size_t,
                                   ctypes.POINTER(ctypes.c_size_t)]
k32.GetModuleHandleW.restype = wt.HMODULE
k32.GetProcAddress.restype = ctypes.c_void_p
k32.GetProcAddress.argtypes = [wt.HMODULE, ctypes.c_char_p]
k32.CreateRemoteThread.restype = wt.HANDLE
k32.CreateRemoteThread.argtypes = [wt.HANDLE, ctypes.c_void_p, ctypes.c_size_t, ctypes.c_void_p,
                                   ctypes.c_void_p, wt.DWORD, ctypes.c_void_p]
k32.GetExitCodeThread.argtypes = [wt.HANDLE, ctypes.POINTER(wt.DWORD)]


def find_pid():
    out = subprocess.run(["tasklist", "/FI", f"IMAGENAME eq {EXE}", "/FO", "CSV", "/NH"],
                         capture_output=True, text=True).stdout
    for line in out.splitlines():
        parts = [p.strip('"') for p in line.split('","')]
        if parts and parts[0].lower() == EXE.lower():
            return int(parts[1])
    return None


def inject(pid, dll):
    path = str(dll).encode("utf-16-le") + b"\0\0"
    h = k32.OpenProcess(0x1F0FFF, False, pid)
    if not h:
        sys.exit(f"OpenProcess failed ({ctypes.get_last_error()})")
    mem = k32.VirtualAllocEx(h, None, len(path), 0x3000, 0x04)
    k32.WriteProcessMemory(h, mem, path, len(path), None)
    load = k32.GetProcAddress(k32.GetModuleHandleW("kernel32.dll"), b"LoadLibraryW")
    t = k32.CreateRemoteThread(h, None, 0, load, mem, 0, None)
    if not t:
        sys.exit(f"CreateRemoteThread failed ({ctypes.get_last_error()})")
    k32.WaitForSingleObject(t, 30000)
    code = wt.DWORD()
    k32.GetExitCodeThread(t, ctypes.byref(code))
    k32.CloseHandle(t)
    k32.CloseHandle(h)
    return code.value  # low 32 bits of the module handle; 0 means LoadLibrary failed


if __name__ == "__main__":
    delay = float(sys.argv[1]) if len(sys.argv) > 1 else 30
    pid = None
    for _ in range(120):
        pid = find_pid()
        if pid:
            break
        time.sleep(1)
    if not pid:
        sys.exit("Game not running.")
    print(f"Found {EXE} (pid {pid}); waiting {delay:.0f}s for it to unpack...")
    time.sleep(delay)
    if find_pid() != pid:
        sys.exit("Game closed before UE4SS could be loaded.")
    result = inject(pid, DLL)
    print("UE4SS loaded." if result else "LoadLibrary returned 0 - UE4SS did not load.")
