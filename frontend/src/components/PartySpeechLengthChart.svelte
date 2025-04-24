<script lang="ts">
	import { Bar } from 'svelte-chartjs';
	import type { ChartData, ChartOptions } from 'chart.js';
	import { onMount } from 'svelte';
	import ChartControls from '$components/ChartControls.svelte';
	import { getPartyColor } from '$lib/colors';

	import {
		Chart as ChartJS,
		BarElement,
		CategoryScale,
		LinearScale,
		Tooltip,
		Legend
	} from 'chart.js';

	ChartJS.register(BarElement, CategoryScale, LinearScale, Tooltip, Legend);

	type SpeechLengthItem = {
		party: string | null;
		avg_length: number;
		count: number;
	};

	let startDate: string = '';
	let endDate: string = '';

	let chartData = {
		labels: [] as string[],
		datasets: [
			{
				label: 'Genomsnittlig anförandelängd',
				data: [] as number[],
				backgroundColor: [] as string[]
			}
		]
	} satisfies ChartData<'bar', number[], string>;

	const options: ChartOptions<'bar'> = {
		responsive: true,
		plugins: {
			legend: { display: false }
		},
		scales: {
			y: {
				beginAtZero: true,
				title: { display: true, text: 'Ord per anförande' }
			}
		}
	};

	async function fetchData() {
		try {
			const url = new URL(import.meta.env.VITE_API_DATA + '/summary/speech-lengths');
			url.searchParams.set('group_by_party', 'true');
			if (startDate) url.searchParams.set('start_date', startDate);
			if (endDate) url.searchParams.set('end_date', endDate);

			const res = await fetch(url.toString());
			if (!res.ok) throw new Error(`Fetch failed: ${res.status}`);
			const result: SpeechLengthItem[] = await res.json();

			chartData.labels = result.map((d) => d.party || 'Neutral');
			chartData.datasets[0].data = result.map((d) => d.avg_length);
			chartData.datasets[0].backgroundColor = result.map((d) => getPartyColor(d.party));
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

<ChartControls {startDate} {endDate} on:update={handleUpdate} />

<Bar data={chartData} {options} />
