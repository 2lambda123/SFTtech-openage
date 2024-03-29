// Copyright 2015-2023 the openage authors. See copying.md for legal info.

#pragma once

#include <optional>

#include "../geometry.h"
#include "../resources/mesh_data.h"

#include "buffer.h"
#include "vertex_array.h"


namespace openage {
namespace renderer {
namespace opengl {

/// The OpenGL class representing geometry to be passed to a draw call.
class GlGeometry final : public Geometry {
public:
	/// The default constructor makes a quad.
	GlGeometry();

	/// Initialize a meshed geometry. Relatively costly, has to initialize GL buffers and copy vertex data.
	explicit GlGeometry(const std::shared_ptr<GlContext> &context, resources::MeshData const &);

	/// Executes a draw command for the geometry on the currently active context.
	/// Assumes bound and valid shader program and all other necessary state.
	void draw() const;

	void update_verts_offset(std::vector<uint8_t> const &, size_t) override;

private:
	/// All the pieces of OpenGL state that represent a mesh.
	struct GlMesh {
		GlBuffer vertices;
		GlVertexArray vao;
		std::optional<GlBuffer> indices;
		std::optional<GLenum> index_type;
		size_t vert_count;
		GLenum primitive;
	};

	/// Data managing GPU memory and interpretation of mesh data.
	/// Only present if the type is a mesh.
	std::optional<GlMesh> mesh;
};

} // namespace opengl
} // namespace renderer
} // namespace openage
