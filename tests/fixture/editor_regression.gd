@tool
extends EditorPlugin
## Enable this script as an EditorPlugin in an isolated fixture project.

class NativeErrorLog extends Logger:
	var error_count: int = 0

	func _log_error(_function: String, _file: String, _line: int, _code: String,
			_rationale: String, _editor_notify: bool, _error_type: int,
			_script_backtraces: Array[ScriptBacktrace]) -> void:
		error_count += 1

	func _log_message(_message: String, error: bool) -> void:
		if error:
			error_count += 1


var _native_errors: NativeErrorLog = NativeErrorLog.new()
var _frames: int = 0
var _checks: int = 0
var _failures: Array[String] = []


func _enter_tree() -> void:
	OS.add_logger(_native_errors)


func _exit_tree() -> void:
	OS.remove_logger(_native_errors)


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
		await _test_search(editor)
		await _test_branch_search(editor)
		_test_clear_view()
	# Flush deferred selection and queued control deletion before editor shutdown.
	for _frame: int in range(3):
		await get_tree().process_frame
	_check_native_errors()
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


func _set_query(panel: Control, text: String) -> void:
	var input: LineEdit = _find_class(panel, "LineEdit") as LineEdit
	input.text = text
	panel.emit_signal("update_requested")


func _navigate_empty(panel: Control, tree: Tree, label: String) -> void:
	panel.emit_signal("text_submitted")
	panel.emit_signal("select_previous_match")
	_check(tree.get_root() == null and tree.get_selected() == null, label)


func _test_search(editor: Node) -> void:
	var model: BehaviorTree = BehaviorTree.new()
	var sequence: BTSequence = BTSequence.new()
	var wait_task: BTWait = BTWait.new()
	sequence.add_child(wait_task)
	sequence.add_child(BTFail.new())
	model.root_task = sequence
	model.take_over_path("res://editor_search.tres")
	editor.call("edit_bt", model, true)
	var task_tree: Node = _find_class(editor, "TaskTree")
	var panel: Control = _find_class(task_tree, "TreeSearchPanel") as Control
	var tree: Tree = _find_class(task_tree, "Tree") as Tree
	var filter: CheckBox = _find_class(panel, "CheckBox") as CheckBox
	panel.show()
	filter.button_pressed = true
	_set_query(panel, "no_such_task")
	_check(not tree.get_root().is_visible_in_tree(), "fresh zero-match filter hides root")
	_set_query(panel, "Wait")
	_check(tree.get_root().get_child(0).visible and not tree.get_root().get_child(1).visible,
		"filter shows only matching branch")
	_set_query(panel, "no_such_task")
	_check(not tree.get_root().get_child(0).visible and not tree.get_root().get_child(1).visible,
		"zero-match filter hides previous results")
	_set_query(panel, "")
	_check(tree.get_root().visible and tree.get_root().get_child(0).visible
		and tree.get_root().get_child(1).visible, "clearing query restores all rows")
	_set_query(panel, "Wait")
	var empty: BehaviorTree = BehaviorTree.new()
	empty.take_over_path("res://editor_search_empty.tres")
	editor.call("edit_bt", empty, true)
	panel.show()
	_navigate_empty(panel, tree, "switching to empty tree invalidates navigation")
	_set_query(panel, "Wait")
	_navigate_empty(panel, tree, "searching empty tree keeps navigation safe")
	editor.call("edit_bt", model, true)
	panel.show()
	_set_query(panel, "Wait")
	panel.emit_signal("text_submitted")
	_check(tree.get_selected() != null and tree.get_selected().get_metadata(0) == wait_task,
		"loading populated tree rebuilds search navigation")
	panel.emit_signal("select_previous_match")
	_check(tree.get_selected().get_metadata(0) == wait_task, "previous match wraps correctly")
	model.root_task = null
	task_tree.call("update_tree")
	for _frame: int in range(3):
		await get_tree().process_frame
	_navigate_empty(panel, tree, "deleting root invalidates search without another query")
	model.root_task = sequence
	task_tree.call("update_tree")
	for _frame: int in range(3):
		await get_tree().process_frame
	panel.emit_signal("text_submitted")
	_check(tree.get_selected() != null and tree.get_selected().get_metadata(0) == wait_task,
		"restoring root rebuilds cached matches")


func _check_native_errors() -> void:
	_check(_native_errors.error_count == 0, "editor operations emit no native errors or warnings")

func _check_filtered_navigation(panel: Control, tree: Tree, matches: Array[BTTask], label: String) -> void:
	var items: Array[TreeItem] = [tree.get_root()]
	var visible_matches: Array[BTTask] = []
	while not items.is_empty():
		var item: TreeItem = items.pop_back()
		var task: BTTask = item.get_metadata(0)
		if matches.has(task):
			if item.is_visible_in_tree():
				visible_matches.append(task)
		elif task is BTFail:
			_check(not item.visible, label + " hides nonmatching row")
		for child: TreeItem in item.get_children():
			items.append(child)
	_check(visible_matches.size() == matches.size(), label + " preserves matching rows")
	tree.deselect_all()
	for signal_name: String in ["text_submitted", "select_previous_match"]:
		var visited: Array[BTTask] = []
		for _match: int in range(matches.size()):
			panel.emit_signal(signal_name)
			var selected: TreeItem = tree.get_selected()
			if selected != null and matches.has(selected.get_metadata(0)):
				var selected_task: BTTask = selected.get_metadata(0)
				if not visited.has(selected_task):
					visited.append(selected_task)
		_check(visited.size() == matches.size(), label + " navigates " + signal_name)


func _test_branch_search(editor: Node) -> void:
	var model: BehaviorTree = BehaviorTree.new()
	var root: BTSequence = BTSequence.new()
	var branch: BTSequence = BTSequence.new()
	var first: BTWait = BTWait.new()
	var second: BTWait = BTWait.new()
	branch.add_child(first)
	branch.add_child(BTFail.new())
	root.add_child(branch)
	root.add_child(second)
	root.add_child(BTFail.new())
	model.root_task = root
	model.take_over_path("res://editor_branch_search.tres")
	editor.call("edit_bt", model, true)
	var task_tree: Node = _find_class(editor, "TaskTree")
	var panel: Control = _find_class(task_tree, "TreeSearchPanel") as Control
	var tree: Tree = _find_class(task_tree, "Tree") as Tree
	panel.show()
	(_find_class(panel, "CheckBox") as CheckBox).button_pressed = true
	_set_query(panel, "Wait")
	var matches: Array[BTTask] = [first, second]
	_check_filtered_navigation(panel, tree, matches, "initial branch")
	# Use the same setter and undo manager as the editor enable/disable action.
	var manager: EditorUndoRedoManager = get_undo_redo()
	var history: UndoRedo = manager.get_history_undo_redo(0)
	for enabled: bool in [false, true]:
		var label: String = "enable branch" if enabled else "disable branch"
		manager.create_action(label, UndoRedo.MERGE_DISABLE, self)
		manager.force_fixed_history()
		manager.add_do_method(branch, "_set_enabled", enabled)
		manager.add_undo_method(branch, "_set_enabled", not enabled)
		manager.commit_action()
		_check(branch.is_enabled() == enabled, label + " changes model")
		_check_filtered_navigation(panel, tree, matches, label)
		history.undo()
		_check(branch.is_enabled() != enabled, label + " undo changes model")
		_check_filtered_navigation(panel, tree, matches, label + " undo")
		history.redo()
		_check(branch.is_enabled() == enabled, label + " redo changes model")
		_check_filtered_navigation(panel, tree, matches, label + " redo")
	# Single-row edits must refresh matches even without recreating the branch.
	manager.create_action("Rename matching task", UndoRedo.MERGE_DISABLE, self)
	manager.force_fixed_history()
	manager.add_do_method(first, "set_custom_name", "Hidden task")
	manager.add_undo_method(first, "set_custom_name", "")
	manager.add_do_method(task_tree, "update_task", first)
	manager.add_undo_method(task_tree, "update_task", first)
	manager.commit_action()
	_check(not tree.get_root().get_child(0).visible, "rename hides branch without matches")
	_check_filtered_navigation(panel, tree, [second], "rename")
	history.undo()
	_check_filtered_navigation(panel, tree, matches, "rename undo")
	history.redo()
	_check(not tree.get_root().get_child(0).visible, "rename redo hides branch without matches")
	_check_filtered_navigation(panel, tree, [second], "rename redo")
	history.clear_history()
	# Inspector edits of the selected task arrive through its changed signal.
	task_tree.call("clear_selection")
	task_tree.call("add_selection", first)
	for _frame: int in range(3):
		await get_tree().process_frame
	first.custom_name = "Wait"
	_check(tree.get_root().get_child(0).visible, "selected name becomes matching")
	first.custom_name = "Hidden task"
	_check(not tree.get_root().get_child(0).visible, "selected name hides nonmatching branch")
	_check_filtered_navigation(panel, tree, [second], "selected name stops matching")
	for _frame: int in range(3):
		await get_tree().process_frame


func _test_clear_view() -> void:
	var model: BehaviorTree = BehaviorTree.new()
	model.root_task = BTWait.new()
	var instance: BTInstance = model.instantiate(self, Blackboard.new(), self, self)
	var data: BehaviorTreeData = BehaviorTreeData.create_from_bt_instance(instance)
	var view: BehaviorTreeView = BehaviorTreeView.new()
	add_child(view)
	view.update_tree(data)
	view.update_interval_msec = 1000000000
	view.update_tree(data)
	var retained_data: WeakRef = weakref(data)
	data = null
	view.clear()
	var display: Tree = _find_class(view, "Tree") as Tree
	_check(display.get_root() == null, "clear removes debugger rows")
	_check(retained_data.get_ref() == null, "clear releases pending snapshot")
	view.update_interval_msec = 0
	view.notification(Node.NOTIFICATION_PROCESS)
	_check(display.get_root() == null, "processing after clear cannot resurrect snapshot")
	model.root_task = BTFail.new()
	var fresh_instance: BTInstance = model.instantiate(self, Blackboard.new(), self, self)
	view.update_tree(BehaviorTreeData.create_from_bt_instance(fresh_instance))
	_check(display.get_root() != null and display.get_root().get_text(0).contains("Fail"),
		"fresh snapshot renders after clear")
	view.clear()
	view.clear()
	view.notification(Node.NOTIFICATION_PROCESS)
	_check(display.get_root() == null, "repeated clear remains empty")
	view.queue_free()
