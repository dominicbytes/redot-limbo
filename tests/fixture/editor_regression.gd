@tool
extends EditorPlugin
## Enable this script as an EditorPlugin in an isolated fixture project.

var _frames: int = 0
var _checks: int = 0
var _failures: Array[String] = []


func _process(_delta: float) -> void:
	_frames += 1
	if _frames == 25:
		set_process(false)
		_run()


func _find_class(node: Node, class_name_to_find: String) -> Node:
	if node.get_class() == class_name_to_find:
		return node
	for child: Node in node.get_children(true):
		var found: Node = _find_class(child, class_name_to_find)
		if found != null:
			return found
	return null


func _check(condition: bool, label: String) -> void:
	_checks += 1
	print("EDITOR_TEST_CHECK ", label, " ", condition)
	if not condition:
		_failures.append(label)
		print("EDITOR_TEST_FAIL ", label)


func _run() -> void:
	var editor: Node = _find_class(get_tree().root, "LimboAIEditor")
	_check(editor != null, "native editor is available")
	if editor != null:
		_test_cross_tab_undo(editor)
	# Flush deferred selection and queued control deletion before editor shutdown.
	for _frame: int in range(3):
		await get_tree().process_frame
	print("LIMBOAI_EDITOR_RESULT ", JSON.stringify({
		"passed": _failures.is_empty(), "checks": _checks, "failures": _failures,
	}))
	while EditorInterface.get_resource_filesystem().is_scanning():
		await get_tree().process_frame
	get_tree().quit(0 if _failures.is_empty() else 1)


func _test_cross_tab_undo(editor: Node) -> void:
	var a: BehaviorTree = BehaviorTree.new()
	var original: BTSequence = BTSequence.new()
	var child: BTWait = BTWait.new()
	original.add_child(child)
	a.root_task = original
	a.take_over_path("res://editor_undo_a.tres")
	var b: BehaviorTree = BehaviorTree.new()
	var other_root: BTSequence = BTSequence.new()
	var other_child: BTFail = BTFail.new()
	other_root.add_child(other_child)
	b.root_task = other_root
	b.take_over_path("res://editor_undo_b.tres")
	editor.call("edit_bt", a, true)
	var task_tree: Node = _find_class(editor, "TaskTree")
	task_tree.call("add_selection", original)
	var palette: Node = null
	for node: Node in editor.get_children():
		if node is PopupPanel:
			palette = _find_class(node, "TaskPalette")
			if palette != null:
				break
	_check(palette != null, "type-change palette is available")
	if palette == null:
		return
	palette.emit_signal("task_selected", "BTSelector")
	var replacement: BTTask = a.root_task
	_check(replacement is BTSelector and replacement.get_child(0) == child,
		"root type change preserves child identity")
	editor.call("edit_bt", b, true)
	var history: UndoRedo = get_undo_redo().get_history_undo_redo(0)
	history.undo()
	_check(a.root_task == original and original.get_child_count() == 1,
		"cross-tab undo restores original root and child count")
	_check(child.get_parent() == original, "undo restores child membership")
	editor.call("edit_bt", b, true)
	history.redo()
	_check(a.root_task == replacement and replacement.get_child_count() == 1,
		"cross-tab redo restores replacement root and child count")
	_check(child.get_parent() == replacement, "redo restores child membership")
	_check(b.root_task == other_root and other_root.get_child(0) == other_child,
		"other tree remains intact after undo and redo")
	history.clear_history()
