class_name LimboAITestRecordCondition
extends BTCondition

@export var variable_name: StringName = &"allowed"


func _tick(_delta: float) -> Status:
	return SUCCESS if bool(blackboard.get_var(variable_name, false, false)) else FAILURE
