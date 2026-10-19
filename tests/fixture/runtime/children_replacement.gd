extends RefCounted

const Action := preload("res://tasks/callback_action.gd")


static func run(fixture: SceneTree) -> void:
	var host := Node.new()
	fixture.root.add_child(host)
	var parent := BTSequence.new()
	var child := Action.new()
	parent.add_child(child)
	parent.initialize(host, Blackboard.new(), host)
	parent.execute(0.016)
	parent.set(&"children", [])
	var passed: bool = parent.get_child_count() == 0 and child.is_root() and child.get_index() == -1 and child.get_parent() == null and child.status == BT.FRESH and child.exits == 1
	parent = null
	var next := BTSequence.new()
	next.add_child(child)
	passed = passed and child.get_parent() == next and child.get_index() == 0
	next.set(&"children", [child])
	passed = passed and next.get_child_count() == 1 and child.get_parent() == next and child.get_index() == 0
	# Replacing the hierarchy from an exit callback must not invalidate abort iteration.
	var sibling := Action.new()
	next.add_child(sibling)
	next.initialize(host, Blackboard.new(), host)
	next.execute(0.016)
	child.callback_phase = &"exit"
	child.callback = next.set.bind(&"children", [])
	next.abort()
	child.callback = Callable()
	passed = passed and child.is_root() and sibling.is_root() and next.get_child_count() == 0
	fixture._record_case("children_replacement_links", passed, {})
	host.free()
