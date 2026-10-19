extends RefCounted

const Action := preload("res://tasks/callback_action.gd")


class ErrorCounter extends Logger:
	var errors: int = 0

	func _log_error(_function: String, _file: String, _line: int, _code: String, _rationale: String, _editor_notify: bool, _error_type: int, _script_backtraces: Array[ScriptBacktrace]) -> void:
		errors += 1


static func run(fixture: SceneTree) -> void:
	await _test_player_context_loss(fixture)
	await _test_state_context_loss(fixture)


static func _test_player_context_loss(fixture: SceneTree) -> void:
	var host := Node.new()
	fixture.root.add_child(host)
	var logger := ErrorCounter.new()
	OS.add_logger(logger)
	Engine.set_print_error_messages(true)
	var passed := true
	var error_counts: Array[int] = []
	for free_agent: bool in [true, false]:
		var agent := Node.new()
		var scene := Node.new()
		host.add_child(agent)
		host.add_child(scene)
		var tree := BehaviorTree.new()
		tree.root_task = Action.new()
		var instance: BTInstance = tree.instantiate(agent, Blackboard.new(), host, scene)
		var action: BTTask = instance.get_root_task()
		var player := BTPlayer.new()
		player.update_mode = BTPlayer.IDLE
		player.set_scene_root_hint(host)
		host.add_child(player)
		player.set_bt_instance(instance)
		player.update(0.016)
		var statuses: Array[int] = []
		var completions: Array[int] = []
		var instance_statuses: Array[int] = []
		player.updated.connect(func(status: int) -> void: statuses.append(status))
		instance.updated.connect(func(status: int) -> void: instance_statuses.append(status))
		if player.has_signal(&"behavior_tree_finished"):
			player.connect(&"behavior_tree_finished", func(status: int) -> void: completions.append(status))
		logger.errors = 0
		if free_agent:
			agent.free()
		else:
			scene.free()
		for frame: int in 4:
			await fixture.process_frame
			player.update(0.016)
			instance.update(0.016)
		# Reactivating an invalid instance must not repeat its failure notification.
		player.set_active(true)
		player.update(0.016)
		error_counts.append(logger.errors)
		passed = passed and logger.errors == 1 and not player.active and action.exits == 1 and statuses == [BT.FAILURE] and instance_statuses == [BT.FAILURE]
		passed = passed and (not player.has_signal(&"behavior_tree_finished") or completions == [BT.FAILURE])
		var replacement: BTInstance = tree.instantiate(host, Blackboard.new(), host, host)
		player.set_bt_instance(replacement)
		player.set_active(true)
		player.update(0.016)
		passed = passed and player.active and replacement.is_instance_valid() and statuses == [BT.FAILURE, BT.RUNNING]
		player.behavior_tree = null
		player.free()
		if is_instance_valid(agent):
			agent.free()
		if is_instance_valid(scene):
			scene.free()
	OS.remove_logger(logger)
	fixture._record_case("player_context_loss", passed, {"error_counts": error_counts})
	host.free()


static func _test_state_context_loss(fixture: SceneTree) -> void:
	var host := Node.new()
	fixture.root.add_child(host)
	var logger := ErrorCounter.new()
	OS.add_logger(logger)
	var passed := true
	var error_counts: Array[int] = []
	for free_agent: bool in [true, false]:
		var agent := Node.new()
		var scene := Node.new()
		host.add_child(agent)
		host.add_child(scene)
		var hsm := LimboHSM.new()
		hsm.update_mode = LimboHSM.MANUAL
		host.add_child(hsm)
		var state := BTState.new()
		var tree := BehaviorTree.new()
		tree.root_task = Action.new()
		state.behavior_tree = tree
		state.set_scene_root_hint(scene)
		hsm.add_child(state)
		hsm.initial_state = state
		var failures: Array[int] = []
		state.add_event_handler(state.failure_event, func() -> bool:
			failures.append(BT.FAILURE)
			return true)
		hsm.initialize(agent)
		hsm.set_active(true)
		hsm.update(0.016)
		var action: BTTask = state.get_bt_instance().get_root_task()
		var updates: Array[float] = []
		state.updated.connect(func(delta: float) -> void: updates.append(delta))
		logger.errors = 0
		if free_agent:
			agent.free()
		else:
			scene.free()
		for frame: int in 4:
			await fixture.process_frame
			hsm.update(0.016)
		error_counts.append(logger.errors)
		passed = passed and logger.errors == 1 and failures == [BT.FAILURE] and updates.size() == 1 and action.exits == 1
		hsm.set_active(false)
		# Reinitialize the installed tree with a valid context before resuming.
		action.initialize(host, state.get_blackboard(), host)
		hsm.set_active(true)
		hsm.update(0.016)
		passed = passed and state.get_bt_instance().is_instance_valid() and state.get_bt_instance().get_last_status() == BT.RUNNING
		hsm.set_active(false)
		hsm.free()
		if is_instance_valid(agent):
			agent.free()
		if is_instance_valid(scene):
			scene.free()
	OS.remove_logger(logger)
	fixture._record_case("state_context_loss", passed, {"error_counts": error_counts})
	host.free()
