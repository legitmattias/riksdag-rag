<!-- src/components/DateCoverage.svelte -->
<script lang="ts">
	export let startDate: string | undefined;
	export let endDate: string | undefined;

	let minDate = '';
	let maxDate = '';
	let isLoading = true;

	import { onMount } from 'svelte';
	import { formatDateSwedish } from '$lib/utils/date';

	onMount(async () => {
		try {
			const res = await fetch(import.meta.env.VITE_API_META + '/date-range');
			const result = await res.json();

			minDate = result.min_date;
			maxDate = result.max_date;

			// Set defaults for start/end if not passed in
			if (!startDate) startDate = minDate;
			if (!endDate) endDate = maxDate;
		} catch (err) {
			console.error('Failed to fetch date range:', err);
		} finally {
			isLoading = false;
		}
	});
</script>

{#if isLoading}
	<p class="text-sm text-gray-500">Laddar datumintervall...</p>
{:else}
	<p class="text-sm text-gray-600">
		{#if minDate && maxDate}
			Databasen innehåller protokoll för tiden <strong>{formatDateSwedish(minDate)}</strong> →
			<strong>{formatDateSwedish(maxDate)}</strong>.<br />
		{/if}

		{#if startDate && endDate}
			Visar anföranden mellan <strong>{formatDateSwedish(startDate)}</strong> och
			<strong>{formatDateSwedish(endDate)}</strong>.
		{/if}
	</p>
{/if}
