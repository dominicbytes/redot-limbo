extends RefCounted

const Action := preload("res://tasks/callback_action.gd")


class FreeContext extends BTAction:
	func _setup() -> void:
		get_scene_root().free()


static func run(fixture: SceneTree) -> void:
	var host := Node.new()
	fixture.root.add_child(host)
	var passed := true
	Engine.set_print_error_messages(false)
	for free_agent: bool in [true, false]:
		var agent := Node.new()
		var scene := Node.new()
		host.add_child(agent)
		host.add_child(scene)
		var tree := BehaviorTree.new()
		tree.root_task = BTFail.new()
		var instance: BTInstance = tree.instantiate(agent, Blackboard.new(), host, scene)
		if free_agent:
			agent.free()
		else:
			scene.free()
		passed = passed and not instance.is_instance_valid() and instance.get_owner_node() == host
		passed = passed and instance.update(0.016) == BT.FAILURE and instance.get_last_status() == BT.FAILURE
		if free_agent:
			passed = passed and instance.get_agent() == null
			scene.free()
		else:
			passed = passed and instance.get_root_task().get_scene_root() == null
			agent.free()
	var setup_scene := Node.new()
	host.add_child(setup_scene)
	var setup_root := BTSequence.new()
	setup_root.add_child(FreeContext.new())
	setup_root.add_child(BTFail.new())
	setup_root.initialize(host, Blackboard.new(), setup_scene)
	passed = passed and setup_root.get_scene_root() == null and setup_root.execute(0.016) == BT.FAILURE
	for phase: StringName in [&"enter", &"tick", &"exit"]:
		var scene := Node.new()
		host.add_child(scene)
		var action := Action.new()
		action.initialize(host, Blackboard.new(), scene)
		action.callback_phase = phase
		action.callback = scene.free
		action.result = BT.SUCCESS if phase == &"exit" else BT.RUNNING
		passed = passed and action.execute(0.016) == BT.FAILURE and action.status == BT.FAILURE and action.exits == 1
		action.callback = Callable()
	for type_name: StringName in [&"BTPauseAnimation", &"BTStopAnimation", &"BTPlayAnimation", &"BTAwaitAnimation"]:
		var player := AnimationPlayer.new()
		player.name = "AnimationPlayer"
		var library := AnimationLibrary.new()
		library.add_animation(&"idle", Animation.new())
		player.add_animation_library(&"", library)
		host.add_child(player)
		var param := BBNode.new()
		param.saved_value = NodePath("AnimationPlayer")
		var task: BTTask = ClassDB.instantiate(type_name) as BTTask
		task.set(&"animation_player", param)
		if type_name in [&"BTPlayAnimation", &"BTAwaitAnimation"]:
			task.set(&"animation_name", &"idle")
		task.initialize(host, Blackboard.new(), host)
		player.free()
		passed = passed and task.execute(0.016) == BT.FAILURE
	Engine.set_print_error_messages(true)
	fixture._record_case("node_lifetime", passed, {})
	host.free()
