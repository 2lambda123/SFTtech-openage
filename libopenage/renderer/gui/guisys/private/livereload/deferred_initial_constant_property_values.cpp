// Copyright 2015-2023 the openage authors. See copying.md for legal info.

#include "deferred_initial_constant_property_values.h"

namespace qtgui {

DeferredInitialConstantPropertyValues::DeferredInitialConstantPropertyValues() :
	init_over{} {
}

DeferredInitialConstantPropertyValues::~DeferredInitialConstantPropertyValues() = default;

void DeferredInitialConstantPropertyValues::apply_static_properties() {
	for (const auto &f : this->static_properties_assignments)
		f();

	this->clear_static_properties();
	this->init_over = true;
}

void DeferredInitialConstantPropertyValues::clear_static_properties() {
	this->static_properties_assignments.clear();
}

bool DeferredInitialConstantPropertyValues::is_init_over() const {
	return this->init_over;
}

} // namespace qtgui
