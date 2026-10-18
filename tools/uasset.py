"""Minimal UE4.22 cooked .uasset/.uexp reader for Minecraft Dungeons.

Reads the name/import/export tables and decodes tagged properties of
export objects (e.g. a blueprint's Default__ CDO) so we can see and patch
enchantment values without the Unreal editor.
"""
import re
import struct
import sys
from pathlib import Path


# Structs serialized as raw binary, not as tagged properties.
NATIVE_STRUCTS = {"Guid", "Rotator", "Quat", "IntPoint", "IntVector", "Vector4", "Box", "Box2D",
                  "SoftObjectPath", "SoftClassPath", "DateTime", "Timespan", "FrameNumber",
                  "PerPlatformFloat", "PerPlatformInt", "MovieSceneFloatChannel", "RichCurveKey",
                  "LevelSequenceObjectReferenceMap", "NavAgentSelector", "FontData"}


class Reader:
    def __init__(self, data, pos=0):
        self.d = data
        self.p = pos

    def i32(self):
        v = struct.unpack_from("<i", self.d, self.p)[0]; self.p += 4; return v

    def u32(self):
        v = struct.unpack_from("<I", self.d, self.p)[0]; self.p += 4; return v

    def i64(self):
        v = struct.unpack_from("<q", self.d, self.p)[0]; self.p += 8; return v

    def f32(self):
        v = struct.unpack_from("<f", self.d, self.p)[0]; self.p += 4; return v

    def u8(self):
        v = self.d[self.p]; self.p += 1; return v

    def raw(self, n):
        v = self.d[self.p:self.p + n]; self.p += n; return v

    def fstring(self):
        n = self.i32()
        if n == 0:
            return ""
        if n > 0:
            s = self.raw(n)[:-1].decode("latin-1")
        else:
            s = self.raw(-n * 2)[:-2].decode("utf-16-le")
        return s


class Package:
    def __init__(self, uasset_path, head=None, body=None):
        self.path = Path(uasset_path)
        self.head = head if head is not None else self.path.read_bytes()
        if body is None:
            uexp = self.path.with_suffix(".uexp")
            body = uexp.read_bytes() if uexp.exists() else b""
        self.body = body
        self.data = self.head + self.body
        self._parse_summary()

    def _parse_summary(self):
        r = Reader(self.head)
        assert r.u32() == 0x9E2A83C1, "not a uasset"
        legacy = r.i32()
        if legacy != -4:
            r.i32()  # LegacyUE3Version
        self.ue4ver = r.i32()
        r.i32()  # licensee
        ncv = r.i32()
        r.raw(ncv * 20)
        self.total_header = r.i32()
        r.fstring()  # folder name
        self.pkg_flags = r.u32()
        name_count, name_off = r.i32(), r.i32()
        r.i32(); r.i32()  # gatherable text
        exp_count, exp_off = r.i32(), r.i32()
        imp_count, imp_off = r.i32(), r.i32()
        self.name_count_pos = name_off_pos = None
        self._summary_tail(r, legacy)

        r.p = name_off
        self.names = []
        for _ in range(name_count):
            self.names.append(r.fstring())
            r.u32()  # hashes

        r.p = imp_off
        self.imports = []
        for _ in range(imp_count):
            cpkg = self.fname(r); cls = self.fname(r); outer = r.i32(); name = self.fname(r)
            self.imports.append((cpkg, cls, outer, name))

        r.p = exp_off
        self.exports = []
        for _ in range(exp_count):
            e = {}
            e["class"] = r.i32(); e["super"] = r.i32(); e["template"] = r.i32(); e["outer"] = r.i32()
            e["name"] = self.fname(r)
            e["flags"] = r.u32()
            e["size_pos"] = r.p
            e["size"] = r.i64(); e["offset"] = r.i64()
            r.raw(12 + 16 + 4 + 8 + 4 + 16)
            self.exports.append(e)

    def _summary_tail(self, r, legacy):
        """Re-walk the summary recording where every offset field lives (for rewriting)."""
        q = Reader(self.head)
        f = self.fields = {}
        q.u32(); q.i32()
        if legacy != -4:
            q.i32()
        q.i32(); q.i32()
        q.raw(q.i32() * 20)
        f["TotalHeaderSize"] = (q.p, "<i"); q.i32()
        q.fstring(); q.u32()
        f["NameCount"] = (q.p, "<i"); q.i32()
        f["NameOffset"] = (q.p, "<i"); q.i32()
        q.i32(); f["GatherableTextDataOffset"] = (q.p, "<i"); q.i32()
        q.i32(); f["ExportOffset"] = (q.p, "<i"); q.i32()
        f["ImportCount"] = (q.p, "<i"); q.i32(); f["ImportOffset"] = (q.p, "<i"); q.i32()
        f["DependsOffset"] = (q.p, "<i"); q.i32()
        q.i32(); f["SoftPackageReferencesOffset"] = (q.p, "<i"); q.i32()
        f["SearchableNamesOffset"] = (q.p, "<i"); q.i32()
        f["ThumbnailTableOffset"] = (q.p, "<i"); q.i32()
        q.raw(16)
        self.generation_name_pos = []
        for _ in range(q.i32()):
            q.i32(); self.generation_name_pos.append(q.p); q.i32()
        for _ in range(2):  # SavedByEngineVersion, CompatibleWithEngineVersion
            q.raw(10); q.fstring()
        q.u32()
        assert q.i32() == 0, "compressed package"
        q.u32()
        for _ in range(q.i32()):
            q.fstring()
        if legacy > -7:
            q.i32()
        f["AssetRegistryDataOffset"] = (q.p, "<i"); q.i32()
        f["BulkDataStartOffset"] = (q.p, "<q"); q.i64()
        f["WorldTileInfoDataOffset"] = (q.p, "<i"); q.i32()
        q.raw(q.i32() * 4)
        q.i32(); f["PreloadDependencyOffset"] = (q.p, "<i"); q.i32()
        self.summary_end = q.p

    def fname(self, r):
        idx = r.i32(); num = r.i32()
        n = self.names[idx] if 0 <= idx < len(self.names) else f"<bad{idx}>"
        return n if num == 0 else f"{n}_{num - 1}"

    def objname(self, index):
        if index < 0:
            return self.imports[-index - 1][3]
        if index > 0:
            return self.exports[index - 1]["name"]
        return "None"

    # ---- tagged properties -------------------------------------------------
    def read_props(self, r, end, depth=0):
        props = []
        while r.p < end:
            tag_start = r.p
            name = self.fname(r)
            if name == "None":
                if depth == 0:
                    self.last_none = r.p - 8
                break
            ptype = self.fname(r)
            size = r.i32(); aidx = r.i32()
            extra = None
            bool_pos = None
            if ptype == "StructProperty":
                extra = self.fname(r); r.raw(16)
            elif ptype == "BoolProperty":
                bool_pos = r.p
                extra = r.u8()
            elif ptype in ("ByteProperty", "EnumProperty"):
                extra = self.fname(r)
            elif ptype in ("ArrayProperty", "SetProperty"):
                extra = self.fname(r)
            elif ptype == "MapProperty":
                extra = (self.fname(r), self.fname(r))
            if r.u8():
                r.raw(16)
            vpos = r.p
            value = self.decode_value(r, ptype, size, extra, depth)
            r.p = vpos + size
            props.append({"name": name, "type": ptype, "index": aidx, "extra": extra,
                          "value": value, "pos": bool_pos if bool_pos is not None else vpos,
                          "size": size, "tag_start": tag_start, "pos_end": vpos + size})
        return props

    def decode_value(self, r, ptype, size, extra, depth):
        p = r.p
        if ptype == "FloatProperty":
            return r.f32()
        if ptype in ("IntProperty",):
            return r.i32()
        if ptype == "BoolProperty":
            return bool(extra)
        if ptype == "ObjectProperty":
            return self.objname(r.i32())
        if ptype in ("NameProperty",):
            return self.fname(r)
        if ptype in ("ByteProperty", "EnumProperty"):
            return self.fname(r) if size == 8 else r.u8()
        if ptype == "StrProperty":
            return r.fstring()
        if ptype == "StructProperty":
            if extra in ("Vector",):
                return struct.unpack_from("<3f", self.data, p)
            if extra in ("Vector2D",):
                return struct.unpack_from("<2f", self.data, p)
            if extra in ("LinearColor",):
                return struct.unpack_from("<4f", self.data, p)
            if extra in ("Color",):
                return tuple(self.data[p:p + 4])
            if extra == "GameplayTagContainer":
                n = r.i32()
                return [self.fname(r) for _ in range(n)]
            if extra == "GameplayTag":
                return self.fname(r)
            if extra in NATIVE_STRUCTS:
                return f"<{extra}>"
            try:
                inner = self.read_props(r, p + size, depth + 1)
            except Exception as ex:  # unknown native struct
                return f"<{extra} {size}b: {ex}>"
            if any(x["name"].startswith("<bad") for x in inner):
                return f"<{extra} {size}b>"
            return inner
        if ptype == "ArrayProperty":
            n = r.i32()
            if extra == "FloatProperty":
                return [r.f32() for _ in range(n)]
            if extra == "IntProperty":
                return [r.i32() for _ in range(n)]
            if extra == "ObjectProperty":
                return [self.objname(r.i32()) for _ in range(n)]
            if extra == "StructProperty":
                # inner tag
                self.fname(r); self.fname(r); r.i32(); r.i32()
                sname = self.fname(r); r.raw(16); r.u8()
                out = []
                for _ in range(n):
                    if sname in ("Vector",):
                        out.append(struct.unpack_from("<3f", self.data, r.p)); r.p += 12
                    elif sname == "RichCurveKey":
                        # InterpMode, TangentMode, TangentWeightMode, Time, Value, tangents...
                        k = struct.unpack_from("<3B6f", self.data, r.p); r.p += 27
                        out.append({"time": k[3], "value": k[4], "interp": k[0],
                                    "arrive": k[5], "leave": k[7]})
                    else:
                        out.append(self.read_props(r, p + size, depth + 1))
                return out
            return f"<array {extra} x{n}>"
        return f"<{ptype} {size}b>"

    def datatable_rows(self, e):
        """Rows of a DataTable export: {row_name: props}."""
        r = Reader(self.data, e["offset"])
        end = e["offset"] + e["size"]
        self.read_props(r, end)
        r.i32()  # object guid flag
        rows = {}
        for _ in range(r.i32()):
            name = self.fname(r)
            rows[name] = self.read_props(r, end)
        return rows

    def export_props(self, e):
        start = e["offset"]
        r = Reader(self.data, start)
        return self.read_props(r, start + e["size"])

    def package_path(self):
        """In-game package path, e.g. /Game/Components/Enchantments/Thorns/BP_Thorns."""
        stem = self.path.stem
        for n in self.names:
            if n.startswith("/") and n.rsplit("/", 1)[-1] == stem:
                return n
        return None

    def cdo(self):
        for e in self.exports:
            if e["name"].startswith("Default__"):
                return e
        return None


def fmt_props(props, indent=0):
    out = []
    pad = "  " * indent
    for p in props:
        v = p["value"]
        label = p["name"] + (f"[{p['index']}]" if p["index"] else "")
        if isinstance(v, list) and v and isinstance(v[0], dict):
            out.append(f"{pad}{label} ({p['extra']}):")
            out += fmt_props(v, indent + 1)
        elif isinstance(v, list) and v and isinstance(v[0], list):
            out.append(f"{pad}{label}: [")
            for item in v:
                out += fmt_props(item, indent + 2); out.append(pad + "    ,")
            out.append(pad + "  ]")
        else:
            if isinstance(v, float):
                v = round(v, 4)
            out.append(f"{pad}{label} = {v}")
    return out


if __name__ == "__main__":
    for path in sys.argv[1:]:
        pkg = Package(path)
        print(f"=== {Path(path).stem}")
        for e in pkg.exports:
            if not e["name"].startswith("Default__"):
                continue
            print(f"  [{e['name']}] parent={pkg.objname(e['class'])}")
            try:
                for line in fmt_props(pkg.export_props(e), 2):
                    print(line)
            except Exception as ex:
                print("    !! parse error", ex)


def parent_class(pkg):
    for e in pkg.exports:
        if e["name"].endswith("_C") and not e["name"].startswith("Default__"):
            return pkg.objname(e["super"])
    return "?"


# --------------------------------------------------------------------------------------------
# Adding properties to an export (used to set values a blueprint doesn't store yet)
# --------------------------------------------------------------------------------------------

def _crc_table(poly, reflected):
    t = []
    for i in range(256):
        if reflected:
            c = i
            for _ in range(8):
                c = (c >> 1) ^ poly if c & 1 else c >> 1
        else:
            c = i << 24
            for _ in range(8):
                c = ((c << 1) ^ poly) & 0xFFFFFFFF if c & 0x80000000 else (c << 1) & 0xFFFFFFFF
        t.append(c)
    return t


_CRC_DEPRECATED = _crc_table(0x04C11DB7, False)
_CRC_SB8 = _crc_table(0xEDB88320, True)


def name_hashes(s):
    """UE4.22 FNameEntrySerialized hashes: (NonCasePreservingHash, CasePreservingHash)."""
    h = 0
    for ch in s:
        h = ((h >> 8) & 0x00FFFFFF) ^ _CRC_DEPRECATED[(h ^ (ord(ch.upper()) & 0xFF)) & 0xFF]
    c = 0xFFFFFFFF
    for ch in s:
        v = ord(ch)
        for _ in range(4):
            c = (c >> 8) ^ _CRC_SB8[(c ^ v) & 0xFF]
            v >>= 8
    return h & 0xFFFF, (c ^ 0xFFFFFFFF) & 0xFFFF


PROP_TYPES = {"float": "FloatProperty", "int": "IntProperty", "bool": "BoolProperty"}


def add_properties(pkg, export_name, props, into_struct=None):
    """Return (new_uasset, new_uexp) with tagged properties appended to an export.

    props: list of (name, type, value), type in float/int/bool. The properties must exist on the
    export's class (here: inherited from its native parent) - the game ignores unknown names.
    into_struct: the name of a struct property of the export that the properties go into instead (its members are
    tagged properties too, ending in None; the struct's size grows with them) - e.g. a bow's AttackDefintion,
    when the bow's file stores only some of its members and inherits the rest.
    """
    exp_i = next(i for i, e in enumerate(pkg.exports) if e["name"] == export_name)
    exp = pkg.exports[exp_i]
    top = pkg.export_props(exp)
    insert_abs = pkg.last_none
    struct_size_pos = None
    if into_struct:
        st = next(x for x in top if x["name"] == into_struct and x["type"] == "StructProperty")
        insert_abs = st["pos_end"] - 8                       # the struct's own None
        struct_size_pos = st["tag_start"] + 16               # tag: name (8), type (8), size (4)
        assert struct.unpack_from("<i", pkg.data, struct_size_pos)[0] == st["size"]
    head, body = bytearray(pkg.head), bytearray(pkg.body)
    assert len(head) == struct.unpack_from("<i", head, pkg.fields["TotalHeaderSize"][0])[0]
    assert exp["offset"] <= insert_abs < exp["offset"] + exp["size"]

    # 1. Names. Unreal stores "foo_2" as name "foo" + number 3, so split numeric suffixes.
    def split(n):
        m = re.match(r"^(.*)_(0|[1-9][0-9]*)$", n)
        return (m.group(1), int(m.group(2)) + 1) if m else (n, 0)

    names = list(pkg.names)
    added = b""
    for n in [split(p[0])[0] for p in props] + [PROP_TYPES[p[1]] for p in props]:
        if n not in names:
            names.append(n)
            raw = n.encode("ascii") + b"\0"
            added += struct.pack("<i", len(raw)) + raw + struct.pack("<HH", *name_hashes(n))
    name_off = struct.unpack_from("<i", head, pkg.fields["NameOffset"][0])[0]
    r = Reader(bytes(head), name_off)
    for _ in range(len(pkg.names)):
        r.fstring(); r.u32()
    name_end = r.p
    dh = len(added)

    def fn(n):
        base, number = split(n)
        return struct.pack("<ii", names.index(base), number)

    # 2. Property tags
    tags = b""
    for name, t, v in props:
        if t == "bool":
            tags += fn(name) + fn("BoolProperty") + struct.pack("<iiBB", 0, 0, 1 if v else 0, 0)
        else:
            tags += fn(name) + fn(PROP_TYPES[t]) + struct.pack("<iiB", 4, 0, 0)
            tags += struct.pack("<f" if t == "float" else "<i", v)
    de = len(tags)
    rel = insert_abs - len(head)
    body[rel:rel] = tags
    if struct_size_pos is not None:
        srel = struct_size_pos - len(head)
        struct.pack_into("<i", body, srel, struct.unpack_from("<i", body, srel)[0] + de)

    # 3. Header: summary offsets past the name map, counts, export table
    for key, (pos, fmt) in pkg.fields.items():
        v = struct.unpack_from(fmt, head, pos)[0]
        if key == "TotalHeaderSize":
            v += dh
        elif key == "NameCount":
            v = len(names)
        elif key == "BulkDataStartOffset":
            v += dh + de if v > 0 else 0
        elif key != "NameOffset" and v >= name_end:
            v += dh
        struct.pack_into(fmt, head, pos, v)
    for pos in pkg.generation_name_pos:
        struct.pack_into("<i", head, pos, len(names))
    for i, e in enumerate(pkg.exports):
        size, off = e["size"], e["offset"] + dh
        if i == exp_i:
            size += de
        elif e["offset"] > exp["offset"]:
            off += de
        struct.pack_into("<qq", head, e["size_pos"], size, off)
    head[name_end:name_end] = added
    return bytes(head), bytes(body)


# --------------------------------------------------------------------------------------------
# Writing nested tagged properties + new imports (used to give gameplay effects new modifiers)
# --------------------------------------------------------------------------------------------
#
# A property tree is a list of nodes:
#   ("Name", "float", 1.5)                 ("Name", "int", 3)          ("Name", "bool", True)
#   ("Name", "str", "text")                ("Name", "name", "FName")
#   ("Name", "object", ImportRef)          ImportRef = (class_package, class_name, outer_ref, object_name)
#   ("Name", "enum", ("EnumType", "EnumType::Value"))        - EnumProperty
#   ("Name", "byteenum", ("EnumType", "EnumType::Value"))    - ByteProperty holding an enum
#   ("Name", "struct", ("StructName", [children]))
#   ("Name", "structarray", ("StructName", [[children], [children], ...]))
# outer_ref of an ImportRef is another ImportRef or a package path string like "/Script/Dungeons".


class _Writer:
    """Collects the names/imports a property tree needs and serializes it."""

    def __init__(self, pkg):
        self.names = list(pkg.names)
        self.new_names = []
        self.imports = list(pkg.imports)  # resolved: (cpkg, cls, outer_index, name)
        self.new_imports = []

    def name(self, n):
        m = re.match(r"^(.*)_(0|[1-9][0-9]*)$", n)
        base, number = (m.group(1), int(m.group(2)) + 1) if m else (n, 0)
        if base not in self.names:
            self.names.append(base)
            self.new_names.append(base)
        return struct.pack("<ii", self.names.index(base), number)

    def import_index(self, ref):
        if isinstance(ref, str):
            key = ("/Script/CoreUObject", "Package", 0, ref)
        else:
            cpkg, cls, outer, obj = ref
            key = (cpkg, cls, self.import_index(outer), obj)
        for i, imp in enumerate(self.imports):
            if imp == key:
                return -(i + 1)
        for part in (key[0], key[1], key[3]):
            self.name(part)
        self.imports.append(key)
        self.new_imports.append(key)
        return -len(self.imports)

    def tag(self, name, ptype, size, extra=b""):
        return self.name(name) + self.name(ptype) + struct.pack("<ii", size, 0) + extra + b"\0"

    def props(self, nodes):
        return b"".join(self.prop(*n) for n in nodes) + self.name("None")

    def prop(self, name, kind, value):
        if kind == "float":
            return self.tag(name, "FloatProperty", 4) + struct.pack("<f", value)
        if kind == "int":
            return self.tag(name, "IntProperty", 4) + struct.pack("<i", value)
        if kind == "bool":
            return self.name(name) + self.name("BoolProperty") + struct.pack("<iiBB", 0, 0, 1 if value else 0, 0)
        if kind == "str":
            raw = value.encode("ascii") + b"\0" if value else b""
            body = struct.pack("<i", len(raw)) + raw
            return self.tag(name, "StrProperty", len(body)) + body
        if kind == "name":
            return self.tag(name, "NameProperty", 8) + self.name(value)
        if kind == "object":
            return self.tag(name, "ObjectProperty", 4) + struct.pack("<i", self.import_index(value))
        if kind in ("enum", "byteenum"):
            enum, val = value
            ptype = "EnumProperty" if kind == "enum" else "ByteProperty"
            return self.tag(name, ptype, 8, self.name(enum)) + self.name(val)
        if kind == "struct":
            sname, children = value
            body = self.props(children)
            return self.tag(name, "StructProperty", len(body), self.name(sname) + b"\0" * 16) + body
        if kind == "structarray":
            sname, elements = value
            elems = b"".join(self.props(e) for e in elements)
            inner = self.tag(name, "StructProperty", len(elems), self.name(sname) + b"\0" * 16)
            body = struct.pack("<i", len(elements)) + inner + elems
            return self.tag(name, "ArrayProperty", len(body), self.name("StructProperty")) + body
        raise ValueError(kind)


def set_export_properties(pkg, export_name, nodes):
    """Return (new_uasset, new_uexp) with property tree `nodes` written into an export.

    Top-level properties the export already has with the same name are replaced; the rest are
    appended. New names and imports are added to the package as needed.
    """
    w = _Writer(pkg)
    exp_i = next(i for i, e in enumerate(pkg.exports) if e["name"] == export_name)
    exp = pkg.exports[exp_i]
    existing = pkg.export_props(exp)
    none_abs = pkg.last_none
    head, body = bytearray(pkg.head), bytearray(pkg.body)
    hlen = len(head)
    assert hlen == struct.unpack_from("<i", head, pkg.fields["TotalHeaderSize"][0])[0]

    # New tag stream: untouched tags byte-for-byte, then the new/replaced ones, then "None" and
    # anything the export serializes after its tags.
    replaced = {n[0].lower() for n in nodes}
    kept = b"".join(bytes(pkg.data[x["tag_start"]:x["pos_end"]])
                    for x in existing if x["name"].lower() not in replaced)
    tail = bytes(pkg.data[none_abs:exp["offset"] + exp["size"]])
    new_export = kept + b"".join(w.prop(*n) for n in nodes) + tail
    rel = exp["offset"] - hlen
    body[rel:rel + exp["size"]] = new_export
    de = len(new_export) - exp["size"]
    return _rewrite_header(pkg, w, head, body, exp_i, de)


def add_imports(pkg, refs):
    """Return (new_uasset, new_uexp, indices): the package with imports `refs` (ImportRefs, see above)
    added if missing, and the package index of each."""
    w = _Writer(pkg)
    indices = [w.import_index(ref) for ref in refs]
    head, body = _rewrite_header(pkg, w, bytearray(pkg.head), bytearray(pkg.body), None, 0)
    return head, body, indices


def _rewrite_header(pkg, w, head, body, exp_i, de):
    """Add the writer's new names/imports to the header and fix every offset; export `exp_i` (if any)
    grew by `de` bytes in the body."""
    hlen = len(head)
    assert hlen == struct.unpack_from("<i", head, pkg.fields["TotalHeaderSize"][0])[0]
    exp = pkg.exports[exp_i] if exp_i is not None else None

    # Serialize new imports first (may add names), then the new name entries.
    added_imports = b""
    for cpkg, cls, outer, obj in w.new_imports:
        added_imports += w.name(cpkg) + w.name(cls) + struct.pack("<i", outer) + w.name(obj)
    added_names = b""
    for n in w.new_names:
        raw = n.encode("ascii") + b"\0"
        added_names += struct.pack("<i", len(raw)) + raw + struct.pack("<HH", *name_hashes(n))
    dh, di = len(added_names), len(added_imports)

    name_off = struct.unpack_from("<i", head, pkg.fields["NameOffset"][0])[0]
    r = Reader(bytes(head), name_off)
    for _ in range(len(pkg.names)):
        r.fstring(); r.u32()
    name_end = r.p
    imp_off = struct.unpack_from("<i", head, pkg.fields["ImportOffset"][0])[0]
    imp_end = imp_off + 28 * len(pkg.imports)
    assert imp_end > name_end

    def shift(v):
        return v + (dh if v >= name_end else 0) + (di if v >= imp_end else 0)

    for key, (pos, fmt) in pkg.fields.items():
        v = struct.unpack_from(fmt, head, pos)[0]
        if key == "TotalHeaderSize":
            v += dh + di
        elif key == "NameCount":
            v = len(w.names)
        elif key == "ImportCount":
            v = len(w.imports)
        elif key == "BulkDataStartOffset":
            v = v + dh + di + de if v > 0 else 0
        elif key != "NameOffset" and v > 0:
            v = shift(v)
        struct.pack_into(fmt, head, pos, v)
    for pos in pkg.generation_name_pos:
        struct.pack_into("<i", head, pos, len(w.names))
    for i, e in enumerate(pkg.exports):
        size, off = e["size"], e["offset"] + dh + di
        if i == exp_i:
            size += de
        elif exp is not None and e["offset"] > exp["offset"]:
            off += de
        struct.pack_into("<qq", head, e["size_pos"], size, off)
    head[imp_end:imp_end] = added_imports
    head[name_end:name_end] = added_names
    return bytes(head), bytes(body)


# --------------------------------------------------------------------------------------------
# Curves
# --------------------------------------------------------------------------------------------

def curve_keys(pkg):
    """[(interp, time, value), ...] of a CurveFloat package, plus the body offset of the key count."""
    exp = pkg.exports[0]
    curve = next(p for p in pkg.export_props(exp) if p["name"] == "FloatCurve")
    keys = next(p for p in curve["value"] if p["name"] == "Keys")
    return [(k["interp"], k["time"], k["value"]) for k in keys["value"]], keys


def clone_curve(pkg, new_name, keys):
    """Return (new_uasset, new_uexp): a copy of CurveFloat package `pkg` renamed to `new_name` (same
    length as the old name, so no offsets move) holding linear `keys` [(time, value), ...]."""
    old_name = pkg.exports[0]["name"]
    assert len(new_name) == len(old_name), "new curve name must be as long as the old one"
    head = bytearray(pkg.head)
    r = Reader(bytes(head), struct.unpack_from("<i", head, pkg.fields["NameOffset"][0])[0])
    for n in pkg.names:
        r.fstring()
        if old_name in n:
            renamed = n.replace(old_name, new_name)
            start = r.p - len(n) - 1
            head[start:start + len(n)] = renamed.encode("ascii")
            struct.pack_into("<HH", head, r.p, *name_hashes(renamed))
        r.u32()

    _, tag = curve_keys(pkg)
    count_pos = tag["pos"] - len(pkg.head)      # i32 key count, then the inner struct tag
    inner_size_pos = count_pos + 4 + 16         # inner tag: name, type, then size
    old_n = struct.unpack_from("<i", pkg.body, count_pos)[0]
    keys_start = count_pos + 4 + 49             # count + inner tag (8+8+4+4+8+16+1)
    raw = b"".join(struct.pack("<3B6f", 0, 0, 0, t, v, 0, 0, 0, 0) for t, v in keys)
    body = bytearray(pkg.body)
    body[keys_start:keys_start + 27 * old_n] = raw
    grow = 27 * (len(keys) - old_n)
    struct.pack_into("<i", body, count_pos, len(keys))
    struct.pack_into("<i", body, inner_size_pos, 27 * len(keys))
    # The Keys array and the FloatCurve struct around it both grew; their sizes sit 8 bytes after
    # their tags' starts (name, type, size).
    curve = next(p for p in pkg.export_props(pkg.exports[0]) if p["name"] == "FloatCurve")
    for p in (tag, curve):
        pos = p["tag_start"] - len(pkg.head) + 16
        struct.pack_into("<i", body, pos, struct.unpack_from("<i", body, pos)[0] + grow)

    e = pkg.exports[0]
    struct.pack_into("<q", head, e["size_pos"], e["size"] + grow)
    pos, fmt = pkg.fields["BulkDataStartOffset"]
    v = struct.unpack_from(fmt, head, pos)[0]
    if v > 0:
        struct.pack_into(fmt, head, pos, v + grow)
    return bytes(head), bytes(body)
