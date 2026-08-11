extends BTAction

@export var result: int = SUCCESS

var entries: int = 0
var ticks: int = 0
var exits: int = 0


func _enter() -> void:
	entries += 1


func _tick(_delta: float) -> Status:
	ticks += 1
	return result


func _exit() -> void:
	exits += 1
