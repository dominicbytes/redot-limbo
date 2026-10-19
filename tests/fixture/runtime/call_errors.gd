extends RefCounted


class Agent extends Node:
	func combine(number: int, text: String) -> String:
		return "%d:%s" % [number, text]

	func delta_result(delta: float, number: int) -> float:
		return delta + number


static func run(fixture: SceneTree) -> void:
	var host := Agent.new()
	fixture.root.add_child(host)
	var bb := Blackboard.new()
	bb.set_var(&"result", "unchanged")
	var node := BBNode.new()
	node.saved_value = NodePath(".")
	var task := BTCallMethod.new()
	task.node = node
	task.result_var = &"result"
	task.initialize(host, bb, host)
	var number := BBVariant.new()
	number.saved_value = 7
	var text := BBVariant.new()
	text.saved_value = "value"
	var passed := true
	Engine.set_print_error_messages(false)
	for method: StringName in [&"missing_method", &"combine"]:
		task.method = method
		passed = passed and task.execute(0.016) == BT.FAILURE and bb.get_var(&"result") == "unchanged"
	task.args = [number, text, number]
	passed = passed and task.execute(0.016) == BT.FAILURE and bb.get_var(&"result") == "unchanged"
	task.method = &"set_process_priority"
	text.saved_value = Vector2.ONE
	task.args = [text]
	passed = passed and task.execute(0.016) == BT.FAILURE and bb.get_var(&"result") == "unchanged"
	Engine.set_print_error_messages(true)
	text.saved_value = "value"
	task.method = &"combine"
	task.args = [number, text]
	passed = passed and task.execute(0.016) == BT.SUCCESS and bb.get_var(&"result") == "7:value"
	task.method = &"delta_result"
	task.args = [number]
	task.args_include_delta = true
	passed = passed and task.execute(0.25) == BT.SUCCESS and bb.get_var(&"result") == 7.25
	fixture._record_case("call_method_errors", passed, {})
	host.free()
