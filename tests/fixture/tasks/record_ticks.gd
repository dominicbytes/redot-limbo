class_name LimboAITestRecordTicks
extends BTAction

@export_range(1, 100, 1) var target_ticks: int = 3
@export var variable_name: StringName = &"ticks"


func _tick(_delta: float) -> Status:
	var ticks: int = int(blackboard.get_var(variable_name, 0, false)) + 1
	blackboard.set_var(variable_name, ticks)
	return SUCCESS if ticks >= target_ticks else RUNNING
