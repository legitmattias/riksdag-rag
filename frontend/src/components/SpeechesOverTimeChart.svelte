<script lang="ts">
	import { Bar } from 'svelte-chartjs';
	import type { ChartData } from 'chart.js';
	import { onMount } from 'svelte';
	import { getPartyColor } from '$lib/colors';
	import { createBaseOptions } from '$lib/chartOptions';

	import {
		Chart as ChartJS,
		BarElement,
		CategoryScale,
		LinearScale,
		Tooltip,
		Legend
	} from 'chart.js';
	import ChartDataLabels from 'chartjs-plugin-datalabels';

	ChartJS.register(BarElement, CategoryScale, LinearScale, Tooltip, Legend, ChartDataLabels);

	export let minimal = false;

	type TimeItem = {
		year: string;
		month?: string;
		party: string | null;
		count: number;
	};

	const apiUrl =
		import.meta.env.VITE_API_DATA +
		'/summary/speeches-over-time?group_by_party=true&resolution=year';

	let chartData: ChartData<'bar', number[], string> = {
		labels: [],
		datasets: []
	};

	let options = {};

	onMount(async () => {
		try {
			const res = await fetch(apiUrl);
			if (!res.ok) throw new Error(`Fetch failed: ${res.status}`);
			const result: TimeItem[] = await res.json();

			const grouped: Record<string, Record<string, number>> = {};
			const years = new Set<string>();

			for (const item of result) {
				const year = item.year;
				const party = item.party || 'Neutral';
				years.add(year);
				grouped[party] ??= {};
				grouped[party][year] = item.count;
			}

			const sortedYears = Array.from(years).sort();
			chartData.labels = sortedYears;

			const datasets = Object.entries(grouped).map(([party, values]) => ({
				label: party,
				backgroundColor: getPartyColor(party),
				data: sortedYears.map((year) => values[year] ?? 0)
			}));

			chartData.datasets = datasets;

			options = createBaseOptions({
				minimal,
				unitLabel: 'anföranden',
				axisLabel: 'Antal anföranden',
				datalabelPosition: 'inside',
				counts: undefined,
				showTooltipCount: false,
				showPartyCode: true
			});
		} catch (err) {
			console.error('Failed to fetch over-time chart data:', err);
		}
	});
</script>

<Bar data={chartData} {options} />
