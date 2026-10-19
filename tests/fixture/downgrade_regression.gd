@tool
extends EditorPlugin
## Enable separately with the editor library on 26.2 to test type-only downgrade.

class ErrorLog extends Logger:
	var messages: Array[String] = []

	func _log_error(_function: String, _file: String, _line: int, code: String,
			rationale: String, _editor_notify: bool, _error_type: int,
			_script_backtraces: Array[ScriptBacktrace]) -> void:
		messages.append(rationale if not rationale.is_empty() else code)


var _frames: int = 0


func _process(_delta: float) -> void:
	_frames += 1
	if _frames == 25:
		set_process(false)
		_run()


func _run() -> void:
	if TYPE_MAX != 39:
		print("LIMBOAI_DOWNGRADE_RESULT ", JSON.stringify({"passed": true, "skipped": true}))
		get_tree().quit()
		return
	var source: String = '[gd_resource type="BBVariant" format=3]\n\n[resource]\ntype = 39\nvalue_source = 1\nvariable = &"struct_value"\n'
	var file: FileAccess = FileAccess.open("user://type-only.tres", FileAccess.WRITE)
	file.store_string(source)
	file.close()
	var logger := ErrorLog.new()
	OS.add_logger(logger)
	var param: BBVariant = ResourceLoader.load("user://type-only.tres", "", ResourceLoader.CACHE_MODE_IGNORE) as BBVariant
	var loaded: bool = param != null and param.type == 39 and param.value_source == BBParam.BLACKBOARD_VAR
	var task := BTSetVar.new()
	task.value = param
	var property: EditorProperty = EditorInterface.get_inspector().instantiate_property_editor(
		task, TYPE_OBJECT, "value", PROPERTY_HINT_RESOURCE_TYPE, "BBVariant", PROPERTY_USAGE_EDITOR)
	get_tree().root.add_child(property)
	property.set_object_and_property(task, "value")
	property.update_property()
	param.value_source = BBParam.SAVED_VALUE
	property.update_property()
	var preserved: bool = param.type == 39 and typeof(param.saved_value) == TYPE_NIL
	var unchanged: bool = FileAccess.get_file_as_string("user://type-only.tres") == source
	var expected: Array[String] = [
		"BBVariant: Variant type 39 is not supported by this runtime; declaration preserved.",
		"BBParam: Variant type 39 is not supported by this runtime; value editor unavailable.",
	]
	OS.remove_logger(logger)
	var passed: bool = loaded and preserved and unchanged and logger.messages == expected
	print("LIMBOAI_DOWNGRADE_RESULT ", JSON.stringify({
		"passed": passed, "loaded": loaded, "declaration_preserved": preserved,
		"resource_unchanged": unchanged, "errors": logger.messages,
	}))
	property.queue_free()
	for _frame: int in range(3):
		await get_tree().process_frame
	while EditorInterface.get_resource_filesystem().is_scanning():
		await get_tree().process_frame
	get_tree().quit(0 if passed else 1)
