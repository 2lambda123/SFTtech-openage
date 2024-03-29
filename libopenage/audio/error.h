// Copyright 2017-2024 the openage authors. See copying.md for legal info.

#pragma once

#include "../error/error.h"

namespace openage {
namespace audio {

class Error : public error::Error {
public:
	Error(const log::message &msg);
};

} // namespace audio
} // namespace openage
