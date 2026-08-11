class_name LimboAITestRecordComposite
extends BTComposite


func _tick(delta: float) -> Status:
	for index in get_child_count():
		var result: Status = get_child(index).execute(delta)
		if result != SUCCESS:
			return result
	return SUCCESS
