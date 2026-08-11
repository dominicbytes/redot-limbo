extends SceneTree

const OUTPUT_PATH := "user://limboai-fixture.pck"


func _initialize() -> void:
	call_deferred(&"_pack")


func _pack() -> void:
	var files: PackedStringArray = []
	_collect_files(ProjectSettings.globalize_path("res://"), "", files)
	for metadata_path in [
		".godot/extension_list.cfg",
		".godot/global_script_class_cache.cfg",
	]:
		if FileAccess.file_exists("res://%s" % metadata_path) and not files.has(metadata_path):
			files.append(metadata_path)
	files.sort()

	var packer := PCKPacker.new()
	var error := packer.pck_start(OUTPUT_PATH)
	if error != OK:
		push_error("Unable to start fixture PCK: %s" % error_string(error))
		quit(2)
		return

	for relative_path in files:
		error = packer.add_file(
			"res://%s" % relative_path,
			ProjectSettings.globalize_path("res://%s" % relative_path)
		)
		if error != OK:
			push_error("Unable to add %s to fixture PCK: %s" % [
				relative_path,
				error_string(error),
			])
			quit(3)
			return

	error = packer.flush()
	if error != OK:
		push_error("Unable to finish fixture PCK: %s" % error_string(error))
		quit(4)
		return

	print("LIMBOAI_FIXTURE_PCK %s files=%d" % [
		ProjectSettings.globalize_path(OUTPUT_PATH),
		files.size(),
	])
	quit(0)


func _collect_files(
	absolute_directory: String,
	relative_directory: String,
	files: PackedStringArray
) -> void:
	var directory := DirAccess.open(absolute_directory)
	if directory == null:
		push_error("Unable to inspect fixture directory: %s" % absolute_directory)
		quit(5)
		return

	directory.list_dir_begin()
	var entry := directory.get_next()
	while not entry.is_empty():
		var relative_path := entry if relative_directory.is_empty() else (
			"%s/%s" % [relative_directory, entry]
		)
		var absolute_path := absolute_directory.path_join(entry)
		if directory.current_is_dir():
			if entry != "." and entry != "..":
				_collect_files(absolute_path, relative_path, files)
		elif not relative_path.begins_with(".godot/") or (
			relative_path == ".godot/extension_list.cfg"
		):
			files.append(relative_path)
		entry = directory.get_next()
	directory.list_dir_end()
