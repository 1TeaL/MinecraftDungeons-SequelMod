"""Shared helpers for the blueprint build scripts: logging, fresh assets, and Graph, which places and wires nodes.

Every step is checked; the first failure stops the script and is written to <script>_out.txt, which
tools/blueprints.py prints.
"""
import os
import unreal

LIB = unreal.SequelEditorLib
tools = unreal.AssetToolsHelpers.get_asset_tools()
assets = unreal.EditorAssetLibrary
log = []
_out = [None]


def start(script_file):
    _out[0] = os.path.splitext(script_file)[0] + "_out.txt"


def write_log():
    with open(_out[0], "w") as f:
        f.write("\n".join(log))


def check(ok, what):
    log.append(("ok   " if ok else "FAIL ") + what)
    write_log()
    if not ok:
        raise RuntimeError(what)


def remove(path):
    if assets.does_asset_exist(path):
        assets.delete_asset(path)
    # delete_asset leaves levels on disk when headless
    level_file = os.path.join(unreal.Paths.project_content_dir(), path[len("/Game/"):] + ".umap")
    if os.path.exists(level_file):
        os.remove(level_file)


def fresh(path, cls, factory):
    remove(path)
    folder, name = path.rsplit("/", 1)
    return tools.create_asset(name, folder, cls, factory)


def blueprint(path, parent):
    factory = unreal.BlueprintFactory()
    factory.set_editor_property("parent_class", parent)
    return fresh(path, unreal.Blueprint, factory)


def compile_save(bp, what):
    msg = LIB.compile(bp)
    check(not msg, what + " compiles " + msg)
    assets.save_loaded_asset(bp)


def widget(wbp, parent, cls, name, is_variable=False):
    """Add a widget to a widget blueprint's tree (parent "" = the root); returns it to set properties on."""
    w = LIB.add_widget(wbp, parent, cls, name, is_variable)
    check(w is not None, "widget " + name)
    return w


def label(wbp, parent, name, words, size=16, is_variable=False):
    t = widget(wbp, parent, unreal.TextBlock, name, is_variable)
    t.set_editor_property("text", unreal.Text(words))
    font = t.get_editor_property("font")
    font.set_editor_property("size", size)
    t.set_editor_property("font", font)
    return t


def level(path, actor_path):
    remove(path)
    check(LIB.make_level(path, [assets.load_blueprint_class(actor_path)]), "level " + path)


class Graph:
    """Builds one graph of a blueprint. Nodes are placed left to right in rows; row() starts a new one."""

    def __init__(self, bp, name="EventGraph"):
        self.bp, self.name, self.x, self.y = bp, name, 0, 0

    def _place(self, node, what):
        check(bool(node), what)
        self.x += 320
        return node

    def row(self, y):
        self.x, self.y = 0, y

    def set(self, node, **pins):
        for pin, value in pins.items():
            check(LIB.set_pin(self.bp, self.name, node, pin, str(value)), node + "." + pin + " = " + str(value))

    def pins(self, node):
        return [line.split(" (")[0] for line in LIB.pins(self.bp, self.name, node).splitlines()]

    def out_pin(self, node, prefix):
        """The one pin whose name starts with prefix, e.g. a cast's "As..." output."""
        found = [p for p in self.pins(node) if p.startswith(prefix)]
        check(len(found) == 1, node + " pin " + prefix + " in " + ", ".join(self.pins(node)))
        return found[0]

    def link(self, a, pa, b, pb):
        check(LIB.link(self.bp, self.name, a, pa, b, pb), a + "." + pa + " -> " + b + "." + pb)

    def flow(self, *steps):
        """Wire exec pins: each step is a node (leaves by "then") or a (node, out pin) pair."""
        prev = None
        for step in steps:
            node, out = step if isinstance(step, tuple) else (step, "then")
            if prev:
                self.link(prev[0], prev[1], node, "execute")
            prev = (node, out)

    # --- nodes ---

    def event(self, owner, name):
        return self._place(LIB.add_event(self.bp, self.name, owner, name, self.x, self.y), "event " + name)

    def custom_event(self, name, params=""):
        return self._place(LIB.add_custom_event(self.bp, self.name, name, params, self.x, self.y), "event " + name)

    def call(self, cls, fn, **pins):
        node = self._place(LIB.add_call(self.bp, self.name, cls, fn, self.x, self.y), "call " + fn)
        self.set(node, **pins)
        return node

    def self_call(self, fn, **pins):
        node = self._place(LIB.add_self_call(self.bp, self.name, fn, self.x, self.y), "call " + fn)
        self.set(node, **pins)
        return node

    def array_call(self, fn, array, array_pin, **links):
        """An array function on array (node, pin); links: item pin name -> (node, pin)."""
        node = self._place(LIB.add_array_call(self.bp, self.name, fn, self.x, self.y), "call " + fn)
        self.link(array[0], array[1], node, "TargetArray")
        for pin, (src, src_pin) in links.items():
            self.link(src, src_pin, node, pin)
        return node

    def macro(self, name, **pins):
        node = self._place(LIB.add_macro(self.bp, self.name, name, self.x, self.y), "macro " + name)
        self.set(node, **pins)
        return node

    def bound_event(self, member, delegate):
        return self._place(LIB.add_bound_event(self.bp, self.name, member, delegate, self.x, self.y),
                           "event " + member + "." + delegate)

    def self_node(self):
        return self.node("/Script/BlueprintGraph.K2Node_Self"), "self"

    def node(self, cls, **props):
        node = self._place(LIB.add_node(self.bp, self.name, cls, self.x, self.y), "node " + cls)
        for prop, value in props.items():
            check(LIB.set_node_property(self.bp, self.name, node, prop, value), node + "." + prop)
        return node

    def cast(self, target, obj=None, cls_cast=False):
        """A cast node; obj (node, pin) is linked in. Returns (node, its As... pin)."""
        kind = "K2Node_ClassDynamicCast" if cls_cast else "K2Node_DynamicCast"
        node = self.node("/Script/BlueprintGraph." + kind, TargetType=target)
        if obj:
            self.link(obj[0], obj[1], node, "Class" if cls_cast else "Object")
        return node, self.out_pin(node, "As")

    def var(self, name, set_=False, owner="", target=None):
        """Get (or set) a variable; owner/target for another object's: target is (node, pin) of that object."""
        node = self._place(LIB.add_member_node(self.bp, self.name, owner, name, set_, self.x, self.y), "var " + name)
        if target:
            self.link(target[0], target[1], node, "self")
        return node

    def item_at(self, array, index=None):
        """array (node, pin)[index (node, pin) or 0]. Returns (node, pin)."""
        node = self.node("/Script/BlueprintGraph.K2Node_GetArrayItem")
        self.link(array[0], array[1], node, "Array")
        if index:
            self.link(index[0], index[1], node, "Dimension 1")
        return node, "Output"

    def branch(self, cond):
        node = self.node("/Script/BlueprintGraph.K2Node_IfThenElse")
        self.link(cond[0], cond[1], node, "Condition")
        return node

    def at_least_zero(self, value):
        node = self.call("/Script/Engine.KismetMathLibrary", "GreaterEqual_IntInt", B=0)
        self.link(value[0], value[1], node, "A")
        return node, "ReturnValue"
