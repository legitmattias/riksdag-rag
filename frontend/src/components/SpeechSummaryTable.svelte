<!-- src/components/SpeechSummaryTable.svelte -->
<script lang="ts">
	import { onMount } from 'svelte';
	import TableControls from '$components/TableControls.svelte';

	type SpeechSummary = {
		speaker: string;
		party?: string;
		date: string;
		clause_title: string;
		speech_number: number;
		length?: number;
	};

	let summaries: SpeechSummary[] = [];
	let isLoading = true;

	let selectedParty: string | undefined = undefined;
	let limit = 25;
	let skip = 0;

	async function fetchSummaries() {
		isLoading = true;
		try {
			const url = new URL(import.meta.env.VITE_API_DATA + '/speeches/summary');
			url.searchParams.set('limit', limit.toString());
			url.searchParams.set('skip', skip.toString());
			if (selectedParty !== undefined) {
				url.searchParams.set('party', selectedParty);
			}

			const res = await fetch(url);
			if (!res.ok) throw new Error(`Fetch failed: ${res.status}`);
			summaries = await res.json();
		} catch (err) {
			console.error('Failed to fetch summaries:', err);
		} finally {
			isLoading = false;
		}
	}

	function updateFilters(event: CustomEvent) {
		selectedParty = event.detail.selectedParty;
		limit = event.detail.limit;
		skip = event.detail.skip;
		fetchSummaries();
	}

	onMount(fetchSummaries);
</script>

<TableControls
	selectedParty={selectedParty ?? '__ALL__'}
	{limit}
	{skip}
	on:update={updateFilters}
/>

{#if isLoading}
	<p class="text-sm text-gray-500">Laddar anföranden...</p>
{:else}
	<div class="overflow-auto">
		<table class="min-w-full border text-sm">
			<thead class="bg-gray-100 text-left">
				<tr>
					<th class="px-4 py-2">Talare</th>
					<th class="px-4 py-2">Parti</th>
					<th class="px-4 py-2">Datum</th>
					<th class="px-4 py-2">Rubrik</th>
					<th class="px-4 py-2">Ord</th>
				</tr>
			</thead>
			<tbody>
				{#each summaries as s}
					<tr class="border-t hover:bg-gray-50">
						<td class="px-4 py-2 font-medium">{s.speaker}</td>
						<td class="px-4 py-2">{s.party || '–'}</td>
						<td class="px-4 py-2">{s.date}</td>
						<td class="px-4 py-2">{s.clause_title}</td>
						<td class="px-4 py-2">{s.length ?? '–'}</td>
					</tr>
				{/each}
			</tbody>
		</table>
	</div>
{/if}
