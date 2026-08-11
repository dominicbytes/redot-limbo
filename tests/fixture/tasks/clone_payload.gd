class_name LimboAITestClonePayload
extends BTAction

@export var payload: Dictionary = {"nested": [1, 2, 3], "label": "original"}


func _tick(_delta: float) -> Status:
	return SUCCESS
