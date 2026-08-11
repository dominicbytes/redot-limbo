class_name LimboAITestRecordDecorator
extends BTDecorator

@export var invert_result: bool = false


func _tick(delta: float) -> Status:
	if get_child_count() != 1:
		return FAILURE
	var result: Status = get_child(0).execute(delta)
	if not invert_result:
		return result
	if result == SUCCESS:
		return FAILURE
	if result == FAILURE:
		return SUCCESS
	return result
