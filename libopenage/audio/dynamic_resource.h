// Copyright 2015-2024 the openage authors. See copying.md for legal info.

#pragma once

#include <atomic>
#include <memory>
#include <tuple>
#include <unordered_map>
#include <vector>

#include "../datastructure/concurrent_queue.h"
#include "../job/job.h"
#include "../job/job_group.h"
#include "../util/path.h"
#include "category.h"
#include "dynamic_loader.h"
#include "format.h"
#include "resource.h"
#include "types.h"

namespace openage {
namespace audio {

/**
 * information storage about a piece of raw audio data.
 */
struct chunk_info_t {
	enum class state_t {
		/** The chunk is currently empty and unused. */
		EMPTY,

		/** The chunk is currently loading. */
		LOADING,

		/** The chunk is loaded and ready to be used. */
		READY
	};

	/** The chunk's current state. */
	std::atomic<state_t> state;

	/** The chunk's count of valid entries (samples). */
	size_t size;

	/** The chunk's buffer. */
	std::unique_ptr<int16_t[]> buffer;

	chunk_info_t(chunk_info_t::state_t state, size_t buffer_size);
	~chunk_info_t() = default;
};


/**
 * Audio data that is loaded dynamically when used.
 */
class DynamicResource : public Resource {
public:
	DynamicResource(AudioManager *manager,
	                category_t category,
	                int id,
	                const util::Path &path,
	                format_t format = format_t::OPUS,
	                int preload_amount = DEFAULT_PRELOAD_AMOUNT,
	                size_t chunk_size = DEFAULT_CHUNK_SIZE,
	                size_t max_chunks = DEFAULT_MAX_CHUNKS);

	virtual ~DynamicResource() = default;

	void use() override;
	void stop_using() override;

	audio_chunk_t get_data(size_t position, size_t data_length) override;

private:
	/**
	 * Start to load audio chunks beginning at the given chunk index.
	 * Continues to do so until the `preload_amount` is reached.
	 */
	void start_preloading(size_t resource_chunk_index);

	/**
	 * Load a single chunk in the background (through the job manager).
	 * First, the given `chunk_info` is invalidated.
	 * Then, after loading, it's pushed into the `decay_queue` so it
	 * can decay again.
	 */
	void load_chunk_async(const std::shared_ptr<chunk_info_t> &chunk_info,
	                      size_t resource_chunk_offset);

public:
	/**
	 * The number of chunks that have to be loaded, before a sound actually
	 * starts playing.
	 */
	static constexpr int DEFAULT_PRELOAD_AMOUNT = 10;

	/** The default used chunk size in bytes (100ms for 48kHz stereo audio). */
	static constexpr size_t DEFAULT_CHUNK_SIZE = 9600 * 2;

	/** The default number of chunks, that can be loaded at the same time. */
	static constexpr size_t DEFAULT_MAX_CHUNKS = 100;

private:
	/** The resource's path. */
	util::Path path;

	/** The resource's audio format. */
	format_t format;

	/** The number of chunks that should be preloaded. */
	int preload_amount;

	/** The size of one audio chunk in bytes. */
	size_t chunk_size;

	/**
	 * The maximum number of chunks that are used to store audio data.
	 * This is the maximum amount stored in the `chunks` map.
	 */
	size_t max_chunks;

	/** The number of sounds that currently use this resource. */
	std::atomic_int use_count;

	/** The background audio loader. */
	std::unique_ptr<DynamicLoader> loader;

	/**
	 * Queue of audio chunk information that manages the decay of buffer data.
	 *
	 * This implements "forget least-recently-used chunks" when a new one
	 * shall be loaded.
	 * This _must_ never run empty! Otherwise the audio system will lock up.
	 */
	datastructure::ConcurrentQueue<std::shared_ptr<chunk_info_t>> decay_queue;

	/**
	 * Resource chunk index to chunk mapping.
	 * Loading and usage state is reached through this.
	 */
	std::unordered_map<size_t, std::shared_ptr<chunk_info_t>> chunks;

	/** The background loading job group. */
	job::JobGroup loading_job_group;
};

} // namespace audio
} // namespace openage
