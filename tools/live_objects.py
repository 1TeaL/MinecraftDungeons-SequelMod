"""Find the game's live objects by vtable, for the launcher's watchers (bonus_watch.py, echo_patch.py, ...).

The game keeps a list of every object it makes (UE4's GUObjectArray; its chunk table is at exe+0x4696848, found
2026-10-12 by looking for the table that holds a known object at its index, +0xC of the object). Every entry is
0x18 bytes and starts with the object's address. Reading the list (about 16 MB) and comparing it with the previous
read takes a few milliseconds, so `poll()` can run several times a second: an enchantment object of a mob that
has just spawned, or of a weapon that has just been equipped, is seen within a fraction of a second.
What is already in the list when the launcher starts is looked through once, beside the passes (about a second),
and again every SWEEP_EVERY seconds (a minute) in case an object was missed.
All 31 kinds the launcher watches are in that list (checked 2026-10-13: items, enchantments, artifacts, prices).

For a kind that is not in the list there is still the scan of the game's whole heap (many seconds; beside the
passes, every FULL_SCAN_EVERY seconds, only for kinds that have not shown themselves in the list).

`refresh()` gives {vtable: [objects]} of everything known that is still alive (still of its kind and, for a kind
in the list, still held by the list - memory of a destroyed object can keep its bytes for a while);
`poll()` gives the same shape with only the objects first seen in the last YOUNG seconds.
"""
import struct
import threading
import time

from endless_patch import find_pointers
from memprobe import read

PAGE = 0x10000
FULL_SCAN_EVERY = 30          # seconds
SWEEP_EVERY = 60              # seconds between looks through the whole object list
YOUNG = 3.0                   # seconds an object counts as new (its owner and tier may be set a moment after it)
OBJECTS = 0x4696848           # the object list: chunk table pointer, -, room, count, chunk room, chunks
ENTRY, CHUNK, BLOCK = 0x18, 0x10000, 0x100       # bytes per entry, entries per chunk, entries compared at a time
INDEX = 0x0C                  # an object's own place in the list


class Scanner:
    def __init__(self, h, base, wait=True):
        """wait: the first refresh() only returns once everything already in the game has been found (what a
        one-off tool wants); the launcher passes False and gets its results as they come in."""
        self.h, self.base = h, base
        self.wait, self.settled = wait, False
        self.vtables = []          # absolute addresses
        self.listed = {}           # vtable -> True once its objects are known to be in the game's object list
        self.known = {}            # object -> vtable
        self.doubt = set()         # known objects that failed the last full pass
        self.found = {}
        self.snapshot = {}         # chunk number -> its bytes at the previous pass
        self.young = {}            # object -> (vtable, first seen)
        self.unsure = []           # objects that were of no watched kind when first seen: looked at once more
        self.jobs = []             # threads at work beside the passes
        self.late = []             # [(vtable, object)] they found, taken over at the next pass
        self.last_full = self.last_sweep = 0.0

    def register(self, offset):
        vt = self.base + offset
        if vt not in self.vtables:
            self.vtables.append(vt)
            self.last_full = 0.0   # a new kind of object: look everywhere at the next pass
            self.settled = False
            if self.snapshot:
                self.beside(self.look_through, dict(self.snapshot), {vt})
        return vt

    # ---- reading objects ---------------------------------------------------------------------------------------
    def heads(self, objects):
        """{object: (its vtable, its place in the object list)}. Objects sharing a memory page are read with one
        read of the page - a level load brings tens of thousands of new objects, the first look through the list
        over half a million."""
        by_page, out = {}, {}
        for o in objects:
            by_page.setdefault(o & ~(PAGE - 1), []).append(o)
        for page, members in by_page.items():
            data = read(self.h, page, PAGE) if len(members) >= 4 else None
            for o in members:
                at = o - page
                raw = data[at:at + 0x10] if data and at + 0x10 <= len(data) else read(self.h, o, 0x10) if o else None
                out[o] = struct.unpack("<Q4xi", raw) if raw and len(raw) == 0x10 else (0, -1)
        return out

    def in_list(self, o, index):
        """True if the game's object list holds this object at the place the object names."""
        data = self.snapshot.get(index // CHUNK) if index >= 0 else None
        at = (index % CHUNK) * ENTRY
        return bool(data) and at + 8 <= len(data) and struct.unpack_from("<Q", data, at)[0] == o

    # ---- work beside the passes --------------------------------------------------------------------------------
    def beside(self, work, *args):
        def run():
            try:
                work(*args)
            except Exception:  # noqa: BLE001 - a bad read (level loading, game closing); the next one tries again
                pass
        t = threading.Thread(target=run, daemon=True)
        self.jobs.append(t)
        t.start()

    def look_through(self, chunks, wanted):
        """Everything in a read of the object list: which of it is of a wanted kind."""
        for data in chunks.values():
            objects = [o for (o,) in struct.iter_unpack("<Q16x", data[:len(data) // ENTRY * ENTRY]) if o]
            for o, (vt, _) in self.heads(objects).items():
                if vt in wanted:
                    self.listed[vt] = True
                    self.late.append((vt, o))

    def heap_scan(self, vtables):
        for vt, objs in find_pointers(self.h, vtables).items():
            heads = self.heads(objs[:200])
            if not self.listed.get(vt) and any(self.in_list(o, heads[o][1]) for o in heads):
                self.listed[vt] = True
            self.late.extend((vt, o) for o in objs)

    def waiting(self):
        """True while work beside the passes (the first look through the list, a heap scan) is under way."""
        self.jobs = [t for t in self.jobs if t.is_alive()]
        return bool(self.jobs)

    # ---- the passes --------------------------------------------------------------------------------------------
    def poll(self):
        """Quick pass: {vtable: [objects first seen in the last YOUNG seconds]}."""
        now = time.time()
        try:
            for vt, o in self.new_objects():
                self.young.setdefault(o, (vt, now))
                self.known[o] = vt
        except (struct.error, TypeError):      # a read failed halfway (level loading): the next pass tries again
            pass
        while self.late:
            vt, o = self.late.pop()
            self.known[o] = vt
        out = {}
        if self.young:
            heads = self.heads(list(self.young))
            for o, (vt, first) in list(self.young.items()):
                if now - first > YOUNG or heads[o][0] != vt:
                    del self.young[o]
                else:
                    out.setdefault(vt, []).append(o)
        if not self.waiting():
            scan = [vt for vt in self.vtables if not self.listed.get(vt)]
            if scan and now - self.last_full >= FULL_SCAN_EVERY:
                self.last_full = now
                self.beside(self.heap_scan, scan)
            elif self.snapshot and now - self.last_sweep >= SWEEP_EVERY:
                self.last_sweep = now
                self.beside(self.look_through, dict(self.snapshot), set(self.vtables))
        return out

    def refresh(self):
        """One full pass: {vtable: [object addresses]} for every registered vtable."""
        if self.wait and not self.settled:
            self.settled = True
            while True:            # the first look through the object list, then the first heap scan if one is due
                self.poll()
                if not self.waiting() and (self.last_full or all(self.listed.get(vt) for vt in self.vtables)):
                    break
                time.sleep(0.05)
        self.poll()
        found = {vt: [] for vt in self.vtables}
        heads = self.heads(list(self.known))
        for o, vt in list(self.known.items()):
            now_vt, index = heads[o]
            if now_vt == vt and vt in found and (not self.listed.get(vt) or self.in_list(o, index)):
                found[vt].append(o)
                self.doubt.discard(o)
            elif o in self.young:
                continue
            elif now_vt not in (0, vt) or o in self.doubt:
                del self.known[o]              # something else lives there now, or it failed twice running
                self.doubt.discard(o)
            else:
                self.doubt.add(o)              # unreadable or not in the list this once: one more chance
        self.found = found
        return self.found

    def new_objects(self):
        """[(vtable, object)] of a registered kind that entered the game's object list since the previous pass."""
        head = read(self.h, self.base + OBJECTS, 0x20)
        table, _, room, count, chunk_room, chunks = struct.unpack("<QQiiii", head)
        if not (table and 0 < count <= room and 0 < chunks <= chunk_room <= 0x400 and count <= chunks * CHUNK):
            return []
        wanted, first, changed = set(self.vtables), not self.snapshot, []
        pointers = struct.unpack(f"<{chunks}Q", read(self.h, table, 8 * chunks))
        for c, at in enumerate(pointers):
            data = read(self.h, at, min(CHUNK, count - c * CHUNK) * ENTRY) if at else None
            if not data:
                continue
            old = self.snapshot.get(c, b"")
            self.snapshot[c] = data
            if first or data == old:
                continue
            step = BLOCK * ENTRY
            for b in range(0, len(data), step):
                if data[b:b + step] == old[b:b + step]:
                    continue
                for i in range(b, min(b + step, len(data)), ENTRY):
                    obj = data[i:i + 8]
                    if obj != old[i:i + 8] and obj != bytes(8):
                        changed.append(struct.unpack("<Q", obj)[0])
        # An object is entered in the list a moment before its constructor has run: one that was of no watched
        # kind when first seen is looked at once more at the next pass.
        again, self.unsure = self.unsure, []
        heads = self.heads(changed + again) if changed or again else {}
        for vt in {vt for vt, _ in heads.values()} & wanted:
            self.listed[vt] = True
        self.unsure = [o for o in changed if heads[o][0] not in wanted][:200000]
        if first:
            # What is already there: looked through once, beside the passes.
            self.last_sweep = time.time()
            self.beside(self.look_through, dict(self.snapshot), wanted)
        return [(vt, o) for o, (vt, _) in heads.items() if vt in wanted]
