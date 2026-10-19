extends RefCounted

const Action := preload("res://tasks/status_action.gd")


static func run(fixture: SceneTree) -> void:
	var host := Node.new()
	fixture.root.add_child(host)
	var bb := Blackboard.new()
	bb.set_var(&"items", [1])
	var each := BTForEach.new()
	each.array_var = &"items"
	each.save_var = &"item"
	var child := Action.new()
	child.result = BT.RUNNING
	each.add_child(child)
	each.initialize(host, bb, host)
	var before: int = each.execute(0.016)
	bb.set_var(&"items", [])
	var after: int = each.execute(0.016)
	var passed: bool = before == BT.RUNNING and after == BT.SUCCESS and child.status == BT.FRESH and child.exits == 1
	each.abort()
	passed = passed and child.exits == 1
	fixture._record_case("foreach_shrink_cleanup", passed, {})
	host.free()
