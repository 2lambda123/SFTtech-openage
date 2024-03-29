// Copyright 2013-2023 the openage authors. See copying.md for legal info.

#include "color.h"

#include <epoxy/gl.h>

namespace openage::util {

void col::use() {
	//TODO use glColor4b
	glColor4f(r / 255.f, g / 255.f, b / 255.f, a / 255.f);
}

void col::use(float alpha) {
	glColor4f(r / 255.f, g / 255.f, b / 255.f, alpha);
}

} // namespace openage::util
