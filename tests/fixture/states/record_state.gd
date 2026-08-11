class_name LimboAITestRecordState
extends LimboState

@export var label: StringName = &"state"


func _setup() -> void:
	_record(&"setup")


func _enter() -> void:
	_record(&"enter")
	if agent != null and agent.has_method(&"record_state_cargo"):
		agent.call(&"record_state_cargo", label, get_cargo())


func _update(_delta: float) -> void:
	_record(&"update")


func _exit() -> void:
	_record(&"exit")


func _record(event: StringName) -> void:
	if agent != null and agent.has_method(&"record_state_event"):
		agent.call(&"record_state_event", label, event)
