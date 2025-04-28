<!-- src/components/SpeechSummaryTable.svelte -->
<script lang="ts">
	import { onMount } from 'svelte';
	import TableControls from '$components/TableControls.svelte';
	import PaginationIndicator from '$components/PaginationIndicator.svelte';
	import SpeechModal from '$components/SpeechModal.svelte';
	import SearchFilters from '$components/SearchFilters.svelte';

	type SpeechSummary = {
		speaker: string;
		party?: string;
		date: string;
		clause_title: string;
		speech_number: number;
		length?: number;
		document_id: string;
	};

	let summaries: SpeechSummary[] = [];
	let isLoading = true;
	let total = 0;
	let selectedSpeechId: string | null = null;
	let showFilters = true;

	// Filters state
	let selectedSpeakers: string[] = [];
	let selectedTopics: string[] = [];
	let matchAllTopics: boolean = false;
	let startDate: string = '';
	let endDate: string = '';

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
			if (selectedSpeakers.length > 0) {
				for (const speaker of selectedSpeakers) {
					url.searchParams.append('speaker', speaker);
				}
			}
			if (selectedTopics.length > 0) {
				for (const topic of selectedTopics) {
					url.searchParams.append('clause_title', topic);
				}
			}
			if (matchAllTopics) {
				url.searchParams.set('match_all', 'true');
			}
			if (startDate) {
				url.searchParams.set('start_date', startDate);
			}
			if (endDate) {
				url.searchParams.set('end_date', endDate);
			}

			const res = await fetch(url);
			if (!res.ok) throw new Error(`Fetch failed: ${res.status}`);
			const result = await res.json();
			summaries = result.items;
			total = result.total;
		} catch (err) {
			console.error('Failed to fetch summaries:', err);
		} finally {
			isLoading = false;
		}
	}

	function handleFilterUpdate(event: CustomEvent) {
		const detail = event.detail;
		selectedSpeakers = detail.speakers || [];
		selectedTopics = detail.topics || [];
		matchAllTopics = detail.matchAll || false;
		startDate = detail.start_date || '';
		endDate = detail.end_date || '';

		skip = 0; // Reset to first page when filters change
		fetchSummaries();
	}

	function updateFilters(event: CustomEvent) {
		const newParty = event.detail.selectedParty;

		// Reset to first page if party changes
		if (newParty !== selectedParty) {
			skip = 0;
		} else {
			skip = event.detail.skip;
		}

		selectedParty = newParty;
		limit = event.detail.limit;

		fetchSummaries();
	}

	onMount(fetchSummaries);
</script>

<div class="mb-4 flex items-center justify-between">
	<button
		class="flex items-center gap-2 rounded bg-blue-600 px-4 py-2 text-white hover:bg-blue-700"
		on:click={() => (showFilters = !showFilters)}
	>
		{showFilters ? 'Dölj filter' : 'Visa filter'}
		<svg
			xmlns="http://www.w3.org/2000/svg"
			class="h-4 w-4 transform transition-transform duration-200"
			fill="none"
			viewBox="0 0 24 24"
			stroke="currentColor"
			stroke-width="2"
			class:rotate-180={showFilters}
		>
			<path stroke-linecap="round" stroke-linejoin="round" d="M19 9l-7 7-7-7" />
		</svg>
	</button>
</div>

{#if showFilters}
	<SearchFilters on:update={handleFilterUpdate} />
{/if}

<TableControls
	selectedParty={selectedParty ?? '__ALL__'}
	{limit}
	{skip}
	{total}
	on:update={updateFilters}
/>

<PaginationIndicator {skip} {limit} {total} />

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
					<th class="px-4 py-2 text-center">Visa anförande</th>
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
						<td class="px-4 py-2 text-center">
							<button
								class="rounded bg-blue-600 px-2 py-1 text-xs text-white transition hover:bg-blue-700"
								on:click={() => (selectedSpeechId = `${s.document_id}_${s.speech_number}`)}
							>
								Visa
							</button>
						</td>
					</tr>
				{/each}
			</tbody>
		</table>
	</div>
{/if}

{#if selectedSpeechId}
	<SpeechModal speechId={selectedSpeechId} onClose={() => (selectedSpeechId = null)} />
{/if}
