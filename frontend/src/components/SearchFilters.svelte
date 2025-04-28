<!-- src/components/SearchFilters.svelte -->
<script lang="ts">
	import { createEventDispatcher, onMount } from 'svelte';

	const dispatch = createEventDispatcher();

	// Filters
	let speakers: string[] = [];
	let topics: string[] = [];
	let matchAll: boolean = false;
	let startDate: string = '';
	let endDate: string = '';

	// Date range from API
	let minDate: string = '';
	let maxDate: string = '';

	let speakerInput = '';
	let topicInput = '';

	async function fetchDateRange() {
		try {
			const res = await fetch(import.meta.env.VITE_API_META + '/date-range');
			const result = await res.json();
			minDate = result.start_date;
			maxDate = result.end_date;
			if (!startDate) startDate = minDate;
			if (!endDate) endDate = maxDate;
		} catch (err) {
			console.error('Failed to fetch date range:', err);
		}
	}

	function addSpeaker() {
		if (speakerInput.trim() && !speakers.includes(speakerInput.trim())) {
			speakers = [...speakers, speakerInput.trim()];
			speakerInput = '';
		}
	}

	function removeSpeaker(s: string) {
		speakers = speakers.filter((item) => item !== s);
	}

	function addTopic() {
		if (topicInput.trim() && !topics.includes(topicInput.trim())) {
			topics = [...topics, topicInput.trim()];
			topicInput = '';
		}
	}

	function removeTopic(t: string) {
		topics = topics.filter((item) => item !== t);
	}

	function applyFilters() {
		dispatch('update', {
			speakers,
			topics,
			matchAll,
			start_date: startDate,
			end_date: endDate
		});
	}

	onMount(fetchDateRange);
</script>

<div class="max-w-3xl space-y-6">
	<div class="mb-6 space-y-6 rounded-lg bg-white p-4 ">
		<div>
			<h3 class="mb-2 text-lg font-semibold">🎤 Talare</h3>
			<div class="mb-2 flex gap-2">
				<input
					type="text"
					placeholder="Lägg till talare..."
					class="flex-1 rounded border p-2"
					bind:value={speakerInput}
					on:keydown={(e) => e.key === 'Enter' && (e.preventDefault(), addSpeaker())}
				/>
				<button
					class="rounded bg-blue-600 px-4 py-2 text-white hover:bg-blue-700"
					on:click={addSpeaker}
				>
					➕
				</button>
			</div>
			<div class="flex flex-wrap gap-2">
				{#each speakers as speaker}
					<span class="rounded bg-gray-200 px-3 py-1 text-sm">
						{speaker}
						<button class="ml-2 text-red-500" on:click={() => removeSpeaker(speaker)}>✖</button>
					</span>
				{/each}
			</div>
		</div>

		<div>
			<h3 class="mb-2 text-lg font-semibold">📝 Rubrik (ämnen)</h3>
			<div class="mb-2 flex gap-2">
				<input
					type="text"
					placeholder="Lägg till ämne..."
					class="flex-1 rounded border p-2"
					bind:value={topicInput}
					on:keydown={(e) => e.key === 'Enter' && (e.preventDefault(), addTopic())}
				/>
				<button
					class="rounded bg-blue-600 px-4 py-2 text-white hover:bg-blue-700"
					on:click={addTopic}
				>
					➕
				</button>
			</div>
			<div class="flex flex-wrap gap-2">
				{#each topics as topic}
					<span class="rounded bg-gray-200 px-3 py-1 text-sm">
						{topic}
						<button class="ml-2 text-red-500" on:click={() => removeTopic(topic)}>✖</button>
					</span>
				{/each}
			</div>

			<div class="mt-2">
				<label class="inline-flex items-center">
					<input type="checkbox" bind:checked={matchAll} class="mr-2" />
					Måste matcha alla ämnen
				</label>
			</div>
		</div>

		<div>
			<h3 class="mb-2 text-lg font-semibold">📅 Datumintervall</h3>
			<div class="flex flex-wrap gap-4">
				<div>
					<label for="start-date" class="block text-sm font-medium text-gray-700">Från</label>
					<input
						id="start-date"
						type="date"
						bind:value={startDate}
						min={minDate}
						max={endDate || maxDate}
						class="mt-1 rounded border p-2"
					/>
				</div>

				<div>
					<label for="end-date" class="block text-sm font-medium text-gray-700">Till</label>
					<input
						id="end-date"
						type="date"
						bind:value={endDate}
						min={startDate || minDate}
						max={maxDate}
						class="mt-1 rounded border p-2"
					/>
				</div>
			</div>
		</div>

		<div>
			<button
				class="mt-4 w-full rounded bg-blue-600 px-4 py-2 text-white hover:bg-blue-700"
				on:click={applyFilters}
			>
				Tillämpa filter
			</button>
		</div>
	</div>
</div>
