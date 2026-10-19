extends RefCounted

const Action := preload("res://tasks/callback_action.gd")
const StatusAction := preload("res://tasks/status_action.gd")


static func run(fixture: SceneTree) -> void:
	var host := Node.new()
	fixture.root.add_child(host)
	var bb := Blackboard.new()
	var passed := true
	var checks := 0
	for phase: StringName in [&"enter", &"tick", &"exit"]:
		for tick: int in [1, 2]:
			for result: int in [BT.RUNNING, BT.SUCCESS, BT.FAILURE]:
				if phase == &"exit" and result == BT.RUNNING:
					continue
				var task := Action.new()
				task.initialize(host, bb, host)
				if tick == 2:
					task.execute(0.016)
				task.result = result
				task.callback_phase = phase
				task.callback_tick = tick
				task.callback = task.abort
				# Enter only happens once per run; use a fresh run for enter callbacks.
				if phase == &"enter" and tick == 2:
					task.abort()
				var exits_before: int = task.exits
				var status: int = task.execute(0.016)
				passed = passed and status == BT.FRESH and task.status == BT.FRESH and task.exits == exits_before + 1
				task.callback = Callable()
				var entries_before: int = task.entries
				task.result = BT.RUNNING
				passed = passed and task.execute(0.016) == BT.RUNNING and task.entries == entries_before + 1
				task.abort()
				checks += 1
	for type_name: StringName in [&"BTSequence", &"BTSelector", &"BTDynamicSequence", &"BTDynamicSelector", &"BTRandomSequence", &"BTRandomSelector", &"BTParallel", &"BTProbabilitySelector"]:
		for tick: int in [1, 2]:
			var composite: BTTask = ClassDB.instantiate(type_name) as BTTask
			var first := Action.new()
			var second := Action.new()
			composite.add_child(first)
			composite.add_child(second)
			composite.initialize(host, bb, host)
			if tick == 2:
				composite.execute(0.016)
			var ticks_before: int = first.ticks + second.ticks
			for child: BTTask in [first, second]:
				child.result = BT.FAILURE if "Selector" in type_name else BT.SUCCESS
				child.callback_tick = child.ticks + 1
				child.callback = composite.abort
			passed = passed and composite.execute(0.016) == BT.FRESH and composite.status == BT.FRESH and first.ticks + second.ticks == ticks_before + 1
			passed = passed and first.status == BT.FRESH and second.status == BT.FRESH
			first.callback = Callable()
			second.callback = Callable()
			checks += 1
	var recursive := Action.new()
	recursive.initialize(host, bb, host)
	recursive.callback = recursive.execute.bind(0.016)
	Engine.set_print_error_messages(false)
	passed = passed and recursive.execute(0.016) == BT.RUNNING and recursive.ticks == 1
	Engine.set_print_error_messages(true)
	recursive.callback = Callable()
	recursive.abort()
	var parallel := BTParallel.new()
	var running := StatusAction.new()
	running.result = BT.RUNNING
	var success := StatusAction.new()
	parallel.add_child(running)
	parallel.add_child(success)
	parallel.num_successes_required = 1
	parallel.initialize(host, bb, host)
	passed = passed and parallel.execute(0.016) == BT.SUCCESS and running.status == BT.RUNNING and running.exits == 0
	parallel.abort()
	passed = passed and running.exits == 1
	var limit := BTTimeLimit.new()
	var limited := StatusAction.new()
	limited.result = BT.RUNNING
	limit.time_limit = 1.0
	limit.add_child(limited)
	limit.initialize(host, bb, host)
	passed = passed and limit.execute(0.0) == BT.RUNNING
	limited.result = BT.SUCCESS
	passed = passed and limit.execute(1.1) == BT.SUCCESS and limited.exits == 1
	limited.result = BT.RUNNING
	passed = passed and limit.execute(0.0) == BT.RUNNING and limit.execute(1.1) == BT.FAILURE and limited.status == BT.FRESH and limited.exits == 2
	fixture._record_case("reentrant_abort", passed, {"callback_checks": checks})
	_test_state_transition(fixture, host)
	_test_cancelled_context_loss(fixture, host)
	host.free()


static func _test_state_transition(fixture: SceneTree, host: Node) -> void:
	var hsm := LimboHSM.new()
	hsm.update_mode = LimboHSM.MANUAL
	host.add_child(hsm)
	var state := BTState.new()
	var idle := LimboState.new()
	var tree := BehaviorTree.new()
	tree.root_task = Action.new()
	state.behavior_tree = tree
	state.set_scene_root_hint(host)
	hsm.add_child(state)
	hsm.add_child(idle)
	hsm.initial_state = state
	hsm.initialize(host)
	hsm.set_active(true)
	var action: BTTask = state.get_bt_instance().get_root_task()
	action.callback = hsm.change_active_state.bind(idle)
	hsm.update(0.016)
	var passed: bool = hsm.get_active_state() == idle and action.status == BT.FRESH and action.exits == 1
	action.callback = Callable()
	hsm.set_active(false)
	fixture._record_case("abort_on_state_transition", passed, {"exits": action.exits})


static func _test_cancelled_context_loss(fixture: SceneTree, host: Node) -> void:
	var scene := Node.new()
	host.add_child(scene)
	var hsm := LimboHSM.new()
	hsm.update_mode = LimboHSM.MANUAL
	host.add_child(hsm)
	var state := BTState.new()
	var idle := LimboState.new()
	var unexpected := LimboState.new()
	var tree := BehaviorTree.new()
	tree.root_task = Action.new()
	state.behavior_tree = tree
	state.failure_event = &"tree_failed"
	state.success_event = &"tree_succeeded"
	state.set_scene_root_hint(scene)
	hsm.add_child(state)
	hsm.add_child(idle)
	hsm.add_child(unexpected)
	hsm.initial_state = state
	hsm.add_transition(idle, unexpected, &"tree_failed")
	hsm.add_transition(idle, unexpected, &"tree_succeeded")
	hsm.initialize(host)
	hsm.set_active(true)
	var action: BTTask = state.get_bt_instance().get_root_task()
	action.callback = func() -> void:
		hsm.change_active_state(idle)
		scene.free()
	hsm.update(0.016)
	var passed: bool = hsm.get_active_state() == idle and action.status == BT.FRESH and action.exits == 1 and state.get_bt_instance().get_last_status() == BT.FRESH
	action.callback = Callable()
	hsm.set_active(false)
	fixture._record_case("cancelled_context_loss", passed, {"exits": action.exits, "status": action.status})
