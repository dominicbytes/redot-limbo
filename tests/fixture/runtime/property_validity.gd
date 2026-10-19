extends RefCounted


class Agent extends Node:
	var nullable: Variant = null


static func run(fixture: SceneTree) -> void:
	var host := Agent.new()
	fixture.root.add_child(host)
	var bb := Blackboard.new()
	var value := BBVariant.new()
	value.saved_value = null
	var check := BTCheckAgentProperty.new()
	check.property = &"nullable"
	check.value = value
	check.initialize(host, bb, host)
	var passed: bool = check.execute(0.016) == BT.SUCCESS
	Engine.set_print_error_messages(false)
	check.property = &"missing_property"
	passed = passed and check.execute(0.016) == BT.FAILURE
	var setter := BTSetAgentProperty.new()
	setter.property = &"missing_property"
	setter.value = value
	setter.initialize(host, bb, host)
	passed = passed and setter.execute(0.016) == BT.FAILURE
	setter.operation = 1
	value.saved_value = 1
	passed = passed and setter.execute(0.016) == BT.FAILURE
	setter.operation = 0
	setter.property = &"process_priority"
	value.saved_value = Vector2.ONE
	passed = passed and setter.execute(0.016) == BT.FAILURE and host.process_priority == 0
	Engine.set_print_error_messages(true)
	value.saved_value = 7
	passed = passed and setter.execute(0.016) == BT.SUCCESS and host.process_priority == 7
	fixture._record_case("agent_property_validity", passed, {})
	host.free()
