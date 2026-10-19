extends BTAction

var result: int = RUNNING
var entries: int = 0
var ticks: int = 0
var exits: int = 0
var callback: Callable
var callback_phase: StringName = &"tick"
var callback_tick: int = 1


func _enter() -> void:
	entries += 1
	if callback_phase == &"enter" and callback.is_valid():
		callback.call()


func _tick(_delta: float) -> Status:
	ticks += 1
	if callback_phase == &"tick" and ticks == callback_tick and callback.is_valid():
		callback.call()
	return result as Status


func _exit() -> void:
	exits += 1
	if callback_phase == &"exit" and callback.is_valid():
		callback.call()
