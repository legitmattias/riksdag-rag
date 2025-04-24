<script lang="ts">
	import { createEventDispatcher, onMount } from 'svelte';

	const dispatch = createEventDispatcher();

	export let startDate: string = '';
	export let endDate: string = '';

	let minDate: string = '';
	let maxDate: string = '';

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

	function applyFilters() {
		dispatch('update', {
			start_date: startDate,
			end_date: endDate
		});
	}

	onMount(fetchDateRange);
</script>

<div class="mb-4 flex flex-wrap items-end gap-4">
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

	<div>
		<button
			on:click={applyFilters}
			class="mt-6 rounded bg-blue-600 px-4 py-2 text-white hover:bg-blue-700"
		>
			Tillämpa
		</button>
	</div>
</div>
