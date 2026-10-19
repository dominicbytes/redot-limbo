extends RefCounted


static func run(fixture: SceneTree) -> void:
	var host := Node.new()
	fixture.root.add_child(host)
	var selector := BTProbabilitySelector.new()
	selector.add_child(BTFail.new())
	selector.add_child(BTFail.new())
	selector.initialize(host, Blackboard.new(), host)
	var passed := true
	Engine.set_print_error_messages(false)
	for invalid: float in [-1.0, NAN, INF, -INF]:
		selector.set_weight(0, invalid)
		passed = passed and selector.get_weight(0) == 1.0 and selector.get_total_weight() == 2.0
		selector.set_probability(0, invalid)
		passed = passed and selector.get_weight(0) == 1.0
		selector.get_child(0).set_meta(&"_weight_", invalid)
		passed = passed and selector.get_weight(0) == 0.0 and selector.get_probability(0) == 0.0 and selector.get_probability(1) == 1.0
		passed = passed and selector.execute(0.016) == BT.FAILURE
		selector.get_child(0).remove_meta(&"_weight_")
	selector.set_weight(0, 1.0e308)
	selector.set_weight(1, 1.0e308)
	passed = passed and selector.get_total_weight() == 0.0 and selector.get_probability(0) == 0.0 and selector.execute(0.016) == BT.FAILURE
	selector.set_weight(0, 0.0)
	selector.set_weight(1, 1.0e308)
	selector.set_probability(0, 0.99)
	passed = passed and selector.get_weight(0) == 0.0
	Engine.set_print_error_messages(true)
	selector.set_weight(1, 0.0)
	passed = passed and selector.get_total_weight() == 0.0 and selector.get_probability(0) == 0.0 and selector.execute(0.016) == BT.FAILURE
	selector.set_weight(0, 1.0)
	selector.set_weight(1, 3.0)
	passed = passed and selector.get_probability(0) == 0.25 and selector.get_probability(1) == 0.75
	fixture._record_case("probability_weight_validation", passed, {})
	host.free()
