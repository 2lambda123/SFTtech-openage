// Copyright 2023-2023 the openage authors. See copying.md for legal info.

#pragma once

#include <cstddef>
#include <memory>
#include <string>


namespace openage::gamestate::activity {
class Node;

using activity_id = size_t;
using activity_label = std::string;

/**
 * Encapsules a self-contained control flow as a node graph.
 */
class Activity {
public:
	/**
     * Create a new activity.
     *
     * @param id Unique ID.
     * @param label Human-readable label (optional).
     * @param start Start node in the graph.
     */
	Activity(activity_id id,
	         activity_label label = "",
	         const std::shared_ptr<Node> &start = nullptr);

	/**
     * Get the unique ID of this activity.
     *
     * @return Unique ID.
     */
	activity_id get_id() const;

	/**
     * Get the human-readable label of this activity.
     *
     * @return Human-readable label.
     */
	const activity_label get_label() const;

	/**
     * Get the start node of this activity.
     *
     * @return Start node.
     */
	const std::shared_ptr<Node> &get_start() const;

private:
	/**
     * Unique ID.
     */
	const activity_id id;

	/**
     * Human-readable label.
     */
	const activity_label label;

	/**
     * Start node.
     */
	std::shared_ptr<Node> start;
};

} // namespace openage::gamestate::activity
