extends RefCounted


static func run(fixture: SceneTree) -> void:
	var host := Node.new()
	fixture.root.add_child(host)
	var disabled := BTFail.new()
	disabled.set("_enabled", false)
	var tree := BehaviorTree.new()
	tree.root_task = disabled
	var subtree := BTSubtree.new()
	subtree.subtree = tree
	subtree.initialize(host, Blackboard.new(), host)
	var status: int = subtree.execute(0.016)
	Engine.set_print_error_messages(false)
	subtree.add_child(null)
	subtree.add_child_at_index(null, 0)
	Engine.set_print_error_messages(true)
	fixture._record_case("disabled_subtree", status == BT.FAILURE and subtree.get_child_count() == 1, {"status": status})
	host.free()
