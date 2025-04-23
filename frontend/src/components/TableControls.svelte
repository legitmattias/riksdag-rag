<!-- src/components/TableControls.svelte -->
<script lang="ts">
	import { createEventDispatcher, onMount } from 'svelte';

	export let selectedParty: string = '__ALL__';
	export let limit: number = 25;
	export let skip: number = 0;
    export let total: number = 0;

	const dispatch = createEventDispatcher();
	let parties: { code: string; label: string }[] = [];

	async function fetchParties() {
		try {
			const res = await fetch(import.meta.env.VITE_API_META + '/parties');
			parties = await res.json();
		} catch (err) {
			console.error('Failed to fetch parties:', err);
		}
	}

	function applyFilters() {
		dispatch('update', {
			selectedParty: selectedParty === '__ALL__' ? undefined : selectedParty,
			limit,
			skip
		});
	}

	function nextPage() {
		skip += limit;
		applyFilters();
	}

	function prevPage() {
		skip = Math.max(skip - limit, 0);
		applyFilters();
	}

	onMount(fetchParties);
</script>

<div class="mb-4 flex flex-wrap items-end gap-4">
	<div>
		<label for="party-select" class="block text-sm font-medium text-gray-700">Parti</label>
		<select
			id="party-select"
			bind:value={selectedParty}
			on:change={applyFilters}
			class="mt-1 min-w-[13rem] rounded border p-2"
		>
			<option value="__ALL__">Alla</option>
			{#each parties.filter((p) => p.code !== '') as p}
				<option value={p.code}>{p.label}</option>
			{/each}
			<option value="">Neutral</option>
		</select>
	</div>

	<div>
		<label for="limit-select" class="block text-sm font-medium text-gray-700">Antal per sida</label>
		<select
			id="limit-select"
			bind:value={limit}
			on:change={applyFilters}
			class="mt-1 min-w-[4rem] rounded border p-2"
		>
			<option value={10}>10</option>
			<option value={25}>25</option>
			<option value={50}>50</option>
		</select>
	</div>

	<div class="mt-4 flex gap-2">
        <button
          on:click={prevPage}
          class="rounded bg-gray-200 px-3 py-1 disabled:opacity-50"
          disabled={skip === 0}
        >
          Föregående
        </button>
        <button
          on:click={nextPage}
          class="rounded bg-gray-200 px-3 py-1 disabled:opacity-50"
          disabled={skip + limit >= total}
        >
          Nästa
        </button>
      </div>
      
</div>
