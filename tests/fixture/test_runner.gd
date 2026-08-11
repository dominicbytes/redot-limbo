extends SceneTree

const RecordTicks := preload("res://tasks/record_ticks.gd")
const RecordCondition := preload("res://tasks/record_condition.gd")
const RecordDecorator := preload("res://tasks/record_decorator.gd")
const RecordComposite := preload("res://tasks/record_composite.gd")
const ClonePayload := preload("res://tasks/clone_payload.gd")
const StatusAction := preload("res://tasks/status_action.gd")
const RecordState := preload("res://states/record_state.gd")

const EXPECTED_CLASSES: PackedStringArray = [
	"BehaviorTree",
	"BTInstance",
	"BTPlayer",
	"BTTask",
	"BTSequence",
	"BTSelector",
	"BTInvert",
	"BTSubtree",
	"Blackboard",
	"BlackboardPlan",
	"LimboState",
	"LimboHSM",
	"BTState",
]
const EXPECTED_EDITOR_CLASSES: PackedStringArray = ["BehaviorTreeView"]

const RESULT_PATH := "user://fixture-result.json"
const TREE_PATH := "user://roundtrip-tree.tres"
const FIXED_DELTA := 0.016

var _cases: Array[Dictionary] = []
var _failures: PackedStringArray = []


class FixtureAgent:
	extends Node

	var state_trace: Array[String] = []
	var cargo_trace: Array[Dictionary] = []

	func record_state_event(state_label: StringName, event: StringName) -> void:
		state_trace.append("%s:%s" % [state_label, event])

	func record_state_cargo(state_label: StringName, cargo: Variant) -> void:
		cargo_trace.append({"state": String(state_label), "cargo": cargo})


func _initialize() -> void:
	call_deferred(&"_run")


func _run() -> void:
	_test_class_registration()
	_test_blackboard_contract()
	_test_blackboard_runtime_inspection()
	var tree: BehaviorTree = _test_resource_roundtrip()
	if tree != null:
		_test_direct_tree_execution(tree)
		_test_clone_deep_copy()
		_test_builtin_task_semantics()
		await _test_bt_player(tree)
		_test_multi_agent_isolation(tree)
		_test_custom_task_categories()
		await _test_hsm_and_bt_state(tree)
		_test_runtime_view_and_performance(tree)
	_write_result()
	quit(0 if _failures.is_empty() else 1)


func _test_class_registration() -> void:
	var expect_editor_classes: bool = ProjectSettings.get_setting(
		"limboai_fixture/expect_editor_classes", true
	)
	var expected_classes := EXPECTED_CLASSES.duplicate()
	if expect_editor_classes:
		expected_classes.append_array(EXPECTED_EDITOR_CLASSES)
	var missing: PackedStringArray = []
	for type_name in expected_classes:
		if not ClassDB.class_exists(type_name):
			missing.append(type_name)
	_record_case("class_registration", missing.is_empty(), {
		"expect_editor_classes": expect_editor_classes,
		"missing": missing,
	})


func _test_blackboard_contract() -> void:
	var parent := Blackboard.new()
	parent.set_var(&"shared", 7)
	var child := Blackboard.new()
	child.set_parent(parent)
	var inherited_before: int = int(child.get_var(&"shared", -1, false))
	child.set_var(&"shared", 9)
	var parent_after: int = int(parent.get_var(&"shared", -1, false))
	var child_after: int = int(child.get_var(&"shared", -1, false))

	var linked := Blackboard.new()
	linked.set_var(&"source", 1)
	child.link_var(&"linked", linked, &"source", true)
	child.set_var(&"linked", 11)
	var linked_after: int = int(linked.get_var(&"source", -1, false))

	var passed: bool = inherited_before == 7 and parent_after == 7 and child_after == 9 and linked_after == 11
	_record_case("blackboard_contract", passed, {
		"inherited_before": inherited_before,
		"parent_after": parent_after,
		"child_after": child_after,
		"linked_after": linked_after,
	})


func _test_blackboard_runtime_inspection() -> void:
	var parent := Blackboard.new()
	parent.set_var(&"shared", 7)
	var child := Blackboard.new()
	child.set_parent(parent)
	child.set_var(&"local", 3)

	var property_names: PackedStringArray = []
	for property: Dictionary in child.get_property_list():
		property_names.append(str(property.get("name", "")))
	var inspected_parent: int = int(child.get(&"scope_1/shared"))
	var inspected_local: int = int(child.get(&"scope_0/local"))
	child.set(&"scope_1/shared", 12)
	var edited_parent: int = int(parent.get_var(&"shared", -1, false))
	var passed: bool = (
		property_names.has("scope_1/shared")
		and property_names.has("scope_0/local")
		and inspected_parent == 7
		and inspected_local == 3
		and edited_parent == 12
	)
	_record_case("blackboard_runtime_inspection", passed, {
		"property_names": property_names,
		"inspected_parent": inspected_parent,
		"inspected_local": inspected_local,
		"edited_parent": edited_parent,
	})


func _test_resource_roundtrip() -> BehaviorTree:
	var plan := BlackboardPlan.new()
	plan.prefetch_nodepath_vars = false
	plan.set("var/ticks/name", "ticks")
	plan.set("var/ticks/type", TYPE_INT)
	plan.set("var/ticks/value", 0)

	var root_task := BTSequence.new()
	root_task.custom_name = "Fixture Root"
	var action := RecordTicks.new()
	action.target_ticks = 3
	action.variable_name = &"ticks"
	root_task.add_child(action)

	var tree := BehaviorTree.new()
	tree.description = "Redot LimboAI deterministic fixture"
	tree.blackboard_plan = plan
	tree.set_root_task(root_task)

	var save_error: Error = ResourceSaver.save(tree, TREE_PATH)
	var loaded: BehaviorTree = ResourceLoader.load(TREE_PATH, "", ResourceLoader.CACHE_MODE_IGNORE) as BehaviorTree
	var loaded_root: BTTask = loaded.get_root_task() if loaded != null else null
	var loaded_action: BTTask = loaded_root.get_child(0) if loaded_root != null and loaded_root.get_child_count() == 1 else null
	var clone: BehaviorTree = loaded.clone() if loaded != null else null
	if clone != null:
		clone.get_root_task().custom_name = "Fixture Root Copy"

	var loaded_blackboard: Blackboard = loaded.blackboard_plan.create_blackboard(null) if loaded != null and loaded.blackboard_plan != null else null
	var semantic_fingerprint := {
		"type": loaded.get_class() if loaded != null else "",
		"description": loaded.description if loaded != null else "",
		"root_type": loaded_root.get_class() if loaded_root != null else "",
		"root_name": loaded_root.custom_name if loaded_root != null else "",
		"child_count": loaded_root.get_child_count() if loaded_root != null else -1,
		"child_script": loaded_action.get_script().resource_path if loaded_action != null else "",
		"target_ticks": loaded_action.target_ticks if loaded_action != null else -1,
		"variable_name": String(loaded_action.variable_name) if loaded_action != null else "",
		"blackboard_ticks": int(loaded_blackboard.get_var(&"ticks", -1, false)) if loaded_blackboard != null else -1,
	}
	var passed: bool = (
		save_error == OK
		and loaded != null
		and loaded.description == tree.description
		and loaded_root != null
		and loaded_root.custom_name == "Fixture Root"
		and loaded_action != null
		and loaded_action.get_script() == RecordTicks
		and semantic_fingerprint.blackboard_ticks == 0
		and clone != null
		and clone.get_root_task().custom_name == "Fixture Root Copy"
		and loaded.get_root_task().custom_name == "Fixture Root"
	)
	_record_case("resource_roundtrip", passed, {
		"save_error": save_error,
		"resource_path": loaded.resource_path if loaded != null else "",
		"root_type": loaded_root.get_class() if loaded_root != null else "",
		"child_script": loaded_action.get_script().resource_path if loaded_action != null else "",
		"clone_name": clone.get_root_task().custom_name if clone != null else "",
		"raw_sha256": FileAccess.get_sha256(TREE_PATH),
		"semantic_fingerprint": semantic_fingerprint,
	})
	return loaded


func _test_direct_tree_execution(tree: BehaviorTree) -> void:
	var host := FixtureAgent.new()
	root.add_child(host)
	var blackboard := Blackboard.new()
	blackboard.set_var(&"ticks", 0)
	var instance: BTInstance = tree.instantiate(host, blackboard, host, host)
	var statuses: Array[int] = []
	for _index in 3:
		statuses.append(instance.update(FIXED_DELTA))
	var ticks: int = int(blackboard.get_var(&"ticks", -1, false))
	var passed: bool = instance.is_instance_valid() and statuses == [BT.RUNNING, BT.RUNNING, BT.SUCCESS] and ticks == 3
	_record_case("direct_tree_execution", passed, {
		"statuses": statuses,
		"ticks": ticks,
		"last_status": instance.get_last_status(),
	})
	host.free()


func _test_clone_deep_copy() -> void:
	var original_action := ClonePayload.new()
	var original_tree := BehaviorTree.new()
	original_tree.set_root_task(original_action)
	var cloned_tree: BehaviorTree = original_tree.clone()
	var cloned_action: BTTask = cloned_tree.get_root_task() if cloned_tree != null else null
	if cloned_action != null:
		cloned_action.payload["nested"][0] = 99
		cloned_action.payload["label"] = "clone"
	var original_nested: int = int(original_action.payload["nested"][0])
	var original_label: String = str(original_action.payload["label"])
	var passed: bool = cloned_action != null and original_nested == 1 and original_label == "original"
	_record_case("clone_deep_copy", passed, {
		"original_nested": original_nested,
		"original_label": original_label,
		"clone_nested": int(cloned_action.payload["nested"][0]) if cloned_action != null else -1,
		"clone_label": str(cloned_action.payload["label"]) if cloned_action != null else "",
	})


func _test_builtin_task_semantics() -> void:
	var agent := Node.new()
	root.add_child(agent)
	var blackboard := Blackboard.new()

	var empty_sequence := BTSequence.new()
	empty_sequence.initialize(agent, blackboard, agent)
	var empty_sequence_status: int = empty_sequence.execute(FIXED_DELTA)

	var sequence := BTSequence.new()
	var sequence_success := StatusAction.new()
	sequence_success.result = BT.SUCCESS
	var sequence_failure := StatusAction.new()
	sequence_failure.result = BT.FAILURE
	var sequence_skipped := StatusAction.new()
	sequence_skipped.result = BT.SUCCESS
	sequence.add_child(sequence_success)
	sequence.add_child(sequence_failure)
	sequence.add_child(sequence_skipped)
	sequence.initialize(agent, blackboard, agent)
	var sequence_status: int = sequence.execute(FIXED_DELTA)

	var selector := BTSelector.new()
	var selector_failure := StatusAction.new()
	selector_failure.result = BT.FAILURE
	var selector_success := StatusAction.new()
	selector_success.result = BT.SUCCESS
	var selector_skipped := StatusAction.new()
	selector_skipped.result = BT.FAILURE
	selector.add_child(selector_failure)
	selector.add_child(selector_success)
	selector.add_child(selector_skipped)
	selector.initialize(agent, blackboard, agent)
	var selector_status: int = selector.execute(FIXED_DELTA)

	var invert := BTInvert.new()
	var invert_child := StatusAction.new()
	invert_child.result = BT.SUCCESS
	invert.add_child(invert_child)
	invert.initialize(agent, blackboard, agent)
	var invert_status: int = invert.execute(FIXED_DELTA)

	var parallel := BTParallel.new()
	parallel.num_successes_required = 1
	parallel.num_failures_required = 1
	var parallel_running_a := StatusAction.new()
	parallel_running_a.result = BT.RUNNING
	var parallel_success := StatusAction.new()
	parallel_success.result = BT.SUCCESS
	var parallel_running_b := StatusAction.new()
	parallel_running_b.result = BT.RUNNING
	parallel.add_child(parallel_running_a)
	parallel.add_child(parallel_success)
	parallel.add_child(parallel_running_b)
	parallel.initialize(agent, blackboard, agent)
	var parallel_status: int = parallel.execute(FIXED_DELTA)

	var wait_ticks := BTWaitTicks.new()
	wait_ticks.num_ticks = 2
	wait_ticks.initialize(agent, blackboard, agent)
	var wait_statuses: Array[int] = [
		wait_ticks.execute(FIXED_DELTA),
		wait_ticks.execute(FIXED_DELTA),
		wait_ticks.execute(FIXED_DELTA),
	]

	var passed: bool = (
		empty_sequence_status == BT.SUCCESS
		and sequence_status == BT.FAILURE
		and sequence_success.ticks == 1
		and sequence_failure.ticks == 1
		and sequence_skipped.status == BT.FRESH
		and selector_status == BT.SUCCESS
		and selector_failure.ticks == 1
		and selector_success.ticks == 1
		and selector_skipped.status == BT.FRESH
		and invert_status == BT.FAILURE
		and parallel_status == BT.SUCCESS
		and wait_statuses == [BT.RUNNING, BT.RUNNING, BT.SUCCESS]
	)
	_record_case("builtin_task_semantics", passed, {
		"empty_sequence": empty_sequence_status,
		"sequence": sequence_status,
		"sequence_child_statuses": [sequence_success.status, sequence_failure.status, sequence_skipped.status],
		"selector": selector_status,
		"selector_child_statuses": [selector_failure.status, selector_success.status, selector_skipped.status],
		"invert": invert_status,
		"parallel": parallel_status,
		"wait_ticks": wait_statuses,
	})
	agent.free()


func _test_bt_player(tree: BehaviorTree) -> void:
	var host := FixtureAgent.new()
	root.add_child(host)
	var player := BTPlayer.new()
	player.active = false
	player.update_mode = BTPlayer.MANUAL
	player.behavior_tree = tree
	player.set_scene_root_hint(host)
	host.add_child(player)
	player.active = true
	await process_frame

	var statuses: Array[int] = []
	player.updated.connect(func(status: int) -> void: statuses.append(status))
	for _index in 3:
		player.update(FIXED_DELTA)
	var ticks: int = int(player.blackboard.get_var(&"ticks", -1, false)) if player.blackboard != null else -1
	var instance: BTInstance = player.get_bt_instance()
	var passed: bool = instance != null and statuses == [BT.RUNNING, BT.RUNNING, BT.SUCCESS] and ticks == 3
	_record_case("bt_player", passed, {
		"statuses": statuses,
		"ticks": ticks,
		"instance_valid": instance.is_instance_valid() if instance != null else false,
	})
	host.free()


func _test_multi_agent_isolation(tree: BehaviorTree) -> void:
	var host := Node.new()
	root.add_child(host)
	var isolated := true
	var snapshots: Array[int] = []
	for index in 32:
		var agent := Node.new()
		agent.name = "Agent%d" % index
		host.add_child(agent)
		var blackboard := Blackboard.new()
		blackboard.set_var(&"ticks", 0)
		var instance: BTInstance = tree.instantiate(agent, blackboard, host, host)
		var status: int = instance.update(FIXED_DELTA)
		var ticks: int = int(blackboard.get_var(&"ticks", -1, false))
		snapshots.append(ticks)
		isolated = isolated and status == BT.RUNNING and ticks == 1
	_record_case("multi_agent_isolation", isolated, {
		"agent_count": snapshots.size(),
		"tick_min": snapshots.min(),
		"tick_max": snapshots.max(),
	})
	host.free()


func _test_custom_task_categories() -> void:
	var agent := Node.new()
	root.add_child(agent)
	var blackboard := Blackboard.new()
	blackboard.set_var(&"allowed", true)

	var composite := RecordComposite.new()
	var decorator := RecordDecorator.new()
	var condition := RecordCondition.new()
	decorator.add_child(condition)
	composite.add_child(decorator)
	composite.initialize(agent, blackboard, agent)
	var success_status: int = composite.execute(FIXED_DELTA)
	decorator.invert_result = true
	composite.abort()
	var inverted_status: int = composite.execute(FIXED_DELTA)
	var passed: bool = success_status == BT.SUCCESS and inverted_status == BT.FAILURE
	_record_case("custom_task_categories", passed, {
		"success_status": success_status,
		"inverted_status": inverted_status,
		"types": [composite.get_script().resource_path, decorator.get_script().resource_path, condition.get_script().resource_path],
	})
	agent.free()


func _test_hsm_and_bt_state(tree: BehaviorTree) -> void:
	var agent := FixtureAgent.new()
	root.add_child(agent)
	var hsm := LimboHSM.new()
	hsm.name = "FixtureHSM"
	hsm.update_mode = LimboHSM.MANUAL
	agent.add_child(hsm)

	var idle := RecordState.new()
	idle.name = "Idle"
	idle.label = &"idle"
	var work := RecordState.new()
	work.name = "Work"
	work.label = &"work"
	var bt_state := BTState.new()
	bt_state.name = "Tree"
	bt_state.behavior_tree = tree
	bt_state.success_event = &"tree_done"
	bt_state.set_scene_root_hint(agent)
	hsm.add_child(idle)
	hsm.add_child(work)
	hsm.add_child(bt_state)
	hsm.initial_state = idle
	hsm.add_transition(idle, work, &"work")
	hsm.add_transition(work, bt_state, &"tree")
	hsm.add_transition(bt_state, idle, &"tree_done")
	hsm.initialize(agent)
	hsm.set_active(true)
	hsm.update(FIXED_DELTA)
	var consumed_work: bool = hsm.dispatch(&"work", 25)
	var cargo_received := false
	for entry: Dictionary in agent.cargo_trace:
		if entry.get("state", "") == "work" and int(entry.get("cargo", -1)) == 25:
			cargo_received = true
			break
	var cargo_cleared: bool = work.get_cargo() == null
	_record_case("hsm_transition_cargo", consumed_work and cargo_received and cargo_cleared, {
		"consumed": consumed_work,
		"received": cargo_received,
		"cleared_after_enter": cargo_cleared,
		"trace": agent.cargo_trace,
	})
	hsm.update(FIXED_DELTA)
	var consumed_tree: bool = hsm.dispatch(&"tree")
	for _index in 3:
		hsm.update(FIXED_DELTA)
	await process_frame
	var leaf_name: String = hsm.get_leaf_state().name if hsm.get_leaf_state() != null else ""
	var passed: bool = consumed_work and consumed_tree and leaf_name == "Idle" and agent.state_trace.has("idle:enter") and agent.state_trace.has("work:enter") and agent.state_trace.has("work:exit")
	_record_case("hsm_and_bt_state", passed, {
		"consumed_work": consumed_work,
		"consumed_tree": consumed_tree,
		"leaf": leaf_name,
		"trace": agent.state_trace,
	})
	hsm.set_active(false)
	agent.free()


func _test_runtime_view_and_performance(tree: BehaviorTree) -> void:
	var expect_editor_classes: bool = ProjectSettings.get_setting(
		"limboai_fixture/expect_editor_classes", true
	)
	var view: Object = null
	if ClassDB.class_exists(&"BehaviorTreeView"):
		view = ClassDB.instantiate(&"BehaviorTreeView")
	var host := Node.new()
	root.add_child(host)
	var start_usec: int = Time.get_ticks_usec()
	var checksum := 0
	for index in 200:
		var agent := Node.new()
		agent.name = "PerfAgent%d" % index
		host.add_child(agent)
		var blackboard := Blackboard.new()
		blackboard.set_var(&"ticks", 0)
		var instance: BTInstance = tree.instantiate(agent, blackboard, host, host)
		instance.monitor_performance = index == 0
		checksum += instance.update(FIXED_DELTA)
	var elapsed_usec: int = Time.get_ticks_usec() - start_usec
	var view_matches_build: bool = (view != null) == expect_editor_classes
	var passed: bool = view_matches_build and checksum == 200 * BT.RUNNING and elapsed_usec > 0
	_record_case("runtime_view_and_performance", passed, {
		"agent_count": 200,
		"elapsed_usec": elapsed_usec,
		"editor_view_available": view != null,
		"expect_editor_classes": expect_editor_classes,
		"status_checksum": checksum,
	})
	if view != null:
		view.free()
	host.free()


func _record_case(case_name: String, passed: bool, details: Dictionary = {}) -> void:
	_cases.append({"name": case_name, "passed": passed, "details": details})
	if not passed:
		_failures.append(case_name)


func _write_result() -> void:
	var result := {
		"schema_version": 1,
		"engine": Engine.get_version_info(),
		"project": ProjectSettings.get_setting("application/config/name", ""),
		"fixed_delta": FIXED_DELTA,
		"passed": _failures.is_empty(),
		"failures": _failures,
		"cases": _cases,
	}
	var file := FileAccess.open(RESULT_PATH, FileAccess.WRITE)
	if file == null:
		push_error("Unable to write fixture result: %s" % FileAccess.get_open_error())
		quit(2)
		return
	file.store_string(JSON.stringify(result, "\t") + "\n")
	file.close()
	print("LIMBOAI_FIXTURE_RESULT %s" % JSON.stringify({"passed": result.passed, "case_count": _cases.size(), "failures": _failures}))
