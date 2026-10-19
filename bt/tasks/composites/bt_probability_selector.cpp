/**
 * bt_probability_selector.cpp
 * =============================================================================
 * Copyright (c) 2023-present Serhii Snitsaruk and the LimboAI contributors.
 *
 * Use of this source code is governed by an MIT-style
 * license that can be found in the LICENSE file or at
 * https://opensource.org/licenses/MIT.
 * =============================================================================
 */

#include "bt_probability_selector.h"

#include "../../../compat/math.h"

double BTProbabilitySelector::_get_weight(Ref<BTTask> p_task) const {
	double weight = p_task->get_meta(LW_NAME(_weight_), 1.0);
	ERR_FAIL_COND_V_MSG(!Math::is_finite(weight) || weight < 0.0, 0.0, "Probability weight must be finite and nonnegative.");
	return weight;
}

double BTProbabilitySelector::get_weight(int p_index) const {
	ERR_FAIL_INDEX_V(p_index, get_child_count(), 0.0);
	ERR_FAIL_COND_V(!get_child(p_index)->is_enabled(), 0.0);
	return _get_weight(p_index);
}

void BTProbabilitySelector::set_weight(int p_index, double p_weight) {
	ERR_FAIL_COND_MSG(!Math::is_finite(p_weight) || p_weight < 0.0, "Probability weight must be finite and nonnegative.");
	ERR_FAIL_INDEX(p_index, get_child_count());
	ERR_FAIL_COND(!get_child(p_index)->is_enabled());
	_set_weight(p_index, p_weight);
}

double BTProbabilitySelector::get_probability(int p_index) const {
	ERR_FAIL_INDEX_V(p_index, get_child_count(), 0.0);
	ERR_FAIL_COND_V(!get_child(p_index)->is_enabled(), 0.0);
	double total = _get_total_weight();
	return total == 0.0 ? 0.0 : _get_weight(p_index) / total;
}

void BTProbabilitySelector::set_probability(int p_index, double p_probability) {
	ERR_FAIL_INDEX(p_index, get_child_count());
	ERR_FAIL_COND(!Math::is_finite(p_probability) || p_probability < 0.0);
	ERR_FAIL_COND(p_probability >= 1.0);
	ERR_FAIL_COND(!get_child(p_index)->is_enabled());

	double others_total = _get_total_weight() - _get_weight(p_index);
	ERR_FAIL_COND(!Math::is_finite(others_total) || others_total < 0.0);
	double others_probability = 1.0 - p_probability;
	if (others_total == 0.0) {
		_set_weight(p_index, p_probability > 0.0 ? 1.0 : 0.0);
	} else {
		double new_total = others_total / others_probability;
		ERR_FAIL_COND(!Math::is_finite(new_total));
		_set_weight(p_index, new_total - others_total);
	}
}

bool BTProbabilitySelector::has_probability(int p_index) const {
	ERR_FAIL_INDEX_V(p_index, get_child_count(), false);
	return get_child(p_index)->is_enabled();
}

void BTProbabilitySelector::set_abort_on_failure(bool p_abort_on_failure) {
	abort_on_failure = p_abort_on_failure;
	emit_changed();
}

bool BTProbabilitySelector::get_abort_on_failure() const {
	return abort_on_failure;
}

void BTProbabilitySelector::_enter() {
	_select_task();
}

void BTProbabilitySelector::_exit() {
	failed_tasks.clear();
	selected_task.unref();
}

BT::Status BTProbabilitySelector::_tick(double p_delta) {
	while (selected_task.is_valid()) {
		Ref<BTTask> child = selected_task;
		Status status = child->execute(p_delta);
		if (_is_execution_cancelled()) {
			return FRESH;
		}
		if (status == FAILURE) {
			if (abort_on_failure) {
				return FAILURE;
			}
			failed_tasks.insert(child);
			_select_task();
		} else { // RUNNING or SUCCESS
			return status;
		}
	}

	return FAILURE;
}

void BTProbabilitySelector::_select_task() {
	selected_task.unref();

	double remaining_tasks_weight = _get_total_weight();
	for (const Ref<BTTask> &task : failed_tasks) {
		remaining_tasks_weight -= _get_weight(task);
	}

	if (remaining_tasks_weight <= 0.0) {
		return;
	}
	double roll = RAND_RANGE(0.0, remaining_tasks_weight);
	for (int i = 0; i < get_child_count(); i++) {
		Ref<BTTask> task = get_child(i);
		if (failed_tasks.has(task)) {
			continue;
		}
		double weight = _get_weight(i);
		if (weight == 0) {
			continue;
		}
		if (roll > weight) {
			roll -= weight;
			continue;
		}

		selected_task = task;
		break;
	}
}

//***** Godot

void BTProbabilitySelector::_bind_methods() {
	ClassDB::bind_method(D_METHOD("get_weight", "child_idx"), &BTProbabilitySelector::get_weight);
	ClassDB::bind_method(D_METHOD("set_weight", "child_idx", "weight"), &BTProbabilitySelector::set_weight);
	ClassDB::bind_method(D_METHOD("get_total_weight"), &BTProbabilitySelector::get_total_weight);
	ClassDB::bind_method(D_METHOD("get_probability", "child_idx"), &BTProbabilitySelector::get_probability);
	ClassDB::bind_method(D_METHOD("set_probability", "child_idx", "probability"), &BTProbabilitySelector::set_probability);
	ClassDB::bind_method(D_METHOD("has_probability", "child_idx"), &BTProbabilitySelector::has_probability);
	ClassDB::bind_method(D_METHOD("get_abort_on_failure"), &BTProbabilitySelector::get_abort_on_failure);
	ClassDB::bind_method(D_METHOD("set_abort_on_failure", "enable"), &BTProbabilitySelector::set_abort_on_failure);

	ADD_PROPERTY(PropertyInfo(Variant::BOOL, "abort_on_failure"), "set_abort_on_failure", "get_abort_on_failure");
}
