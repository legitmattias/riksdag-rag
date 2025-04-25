<script lang="ts">
	import { Bar } from 'svelte-chartjs';
	import type { ChartData } from 'chart.js';
	import { onMount } from 'svelte';

	import ChartControls from '$components/ChartControls.svelte';
	import { getPartyColor } from '$lib/colors';
	import { createBaseOptions } from '$lib/chartOptions';

	type SpeechLengthItem = {
		party: string | null;
		avg_length: number;
		count: number;
	};

	let startDate = '';
	let endDate = '';
	let counts: number[] = [];
	let options = {};

	export let minimal = false;

	let chartData = {
		labels: [] as string[],
		datasets: [
			{
				label: 'Genomsnittlig längd',
				data: [] as number[],
				backgroundColor: [] as string[]
			}
		]
	} satisfies ChartData<'bar', number[], string>;

	async function fetchData() {
		try {
			const url = new URL(import.meta.env.VITE_API_DATA + '/summary/speech-lengths');
			url.searchParams.set('group_by_party', 'true');
			if (startDate) url.searchParams.set('start_date', startDate);
			if (endDate) url.searchParams.set('end_date', endDate);

			const res = await fetch(url.toString());
			if (!res.ok) throw new Error(`Fetch failed: ${res.status}`);
			const result: SpeechLengthItem[] = await res.json();

			counts = result.map((d) => d.count);
			chartData.labels = result.map((d) => d.party || 'Neutral');
			chartData.datasets[0].data = result.map((d) => d.avg_length);
			chartData.datasets[0].backgroundColor = result.map((d) => getPartyColor(d.party));

			options = createBaseOptions({
				minimal,
				unitLabel: 'ord/anfr.',
				axisLabel: 'Ord per anförande',
				datalabelPosition: 'above',
				showTooltipCount: false
			});
		} catch (err) {
			console.error('Failed to fetch chart data:', err);
		}
	}

	function handleUpdate(e: CustomEvent) {
		startDate = e.detail.start_date;
		endDate = e.detail.end_date;
		fetchData();
	}

	onMount(fetchData);
</script>

{#if !minimal}
	<ChartControls {startDate} {endDate} on:update={handleUpdate} />
{/if}

<Bar data={chartData} {options} />
