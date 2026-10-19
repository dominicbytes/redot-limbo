extends RefCounted

const Action := preload("res://tasks/callback_action.gd")


static func run(fixture: SceneTree) -> void:
	var host := Node.new()
	fixture.root.add_child(host)
	var player := BTPlayer.new()
	player.update_mode = BTPlayer.MANUAL
	player.set_scene_root_hint(host)
	host.add_child(player)
	var plan := BlackboardPlan.new()
	plan.set("var/health/name", "health")
	plan.set("var/health/type", TYPE_INT)
	plan.set("var/health/value", 42)
	plan.set("var/retained/name", "retained")
	plan.set("var/retained/type", TYPE_INT)
	plan.set("var/retained/value", 7)
	var tree := BehaviorTree.new()
	tree.blackboard_plan = plan
	tree.root_task = Action.new()
	player.blackboard.set_var(&"retained", 99)
	player.behavior_tree = tree
	var passed: bool = player.get_bt_instance() != null and player.blackboard.get_var(&"health", -1, false) == 42 and player.blackboard.get_var(&"retained") == 99 and player.blackboard_plan.is_derived()
	fixture._record_case("late_player_tree_defaults", passed, {})
	for mode: int in [0, 1, 2, 3, 4]:
		player.behavior_tree = null
		player.behavior_tree = tree
		player.update(0.016)
		var previous: BTTask = player.get_bt_instance().get_root_task()
		var next := BehaviorTree.new()
		next.root_task = BTFail.new()
		if mode == 0:
			player.behavior_tree = next
		elif mode == 1:
			player.behavior_tree = null
		elif mode == 2:
			player.set_bt_instance(next.instantiate(host, Blackboard.new(), host, host))
		else:
			var chosen := BehaviorTree.new()
			chosen.root_task = BTFail.new()
			previous.callback_phase = &"exit"
			previous.callback = player.set_behavior_tree.bind(chosen)
			if mode == 3:
				player.behavior_tree = next
			else:
				player.set_bt_instance(next.instantiate(host, Blackboard.new(), host, host))
			passed = passed and player.behavior_tree == chosen
			previous.callback = Callable()
		passed = passed and previous.status == BT.FRESH and previous.exits == 1
	player.behavior_tree = tree
	var during_tick: BTTask = player.get_bt_instance().get_root_task()
	var replacement := BehaviorTree.new()
	replacement.root_task = BTFail.new()
	during_tick.callback = player.set_behavior_tree.bind(replacement)
	player.update(0.016)
	passed = passed and during_tick.status == BT.FRESH and during_tick.exits == 1 and player.behavior_tree == replacement
	during_tick.callback = Callable()
	var explicit_instance: BTInstance = tree.instantiate(host, Blackboard.new(), host, host)
	player.set_bt_instance(explicit_instance)
	player.update(0.016)
	var explicit_root: BTTask = explicit_instance.get_root_task()
	player.behavior_tree = null
	passed = passed and player.get_bt_instance() == null and explicit_root.status == BT.FRESH and explicit_root.exits == 1
	fixture._record_case("player_tree_replacement_cleanup", passed, {})
	host.free()
