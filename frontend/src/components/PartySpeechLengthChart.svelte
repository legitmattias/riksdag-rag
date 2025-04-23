<!-- src/components/PartySpeechLengthChart.svelte -->
<script lang="ts">
	import { Bar } from 'svelte-chartjs';
	import type { ChartData, ChartOptions } from 'chart.js';
	import { onMount } from 'svelte';
	import { getPartyColor } from '$lib/colors';

	import {
		Chart as ChartJS,
		BarElement,
		CategoryScale,
		LinearScale,
		Tooltip,
		Legend
	} from 'chart.js';

	// Register required Chart.js components
	ChartJS.register(BarElement, CategoryScale, LinearScale, Tooltip, Legend);

	type SpeechLengthItem = {
		party: string | null;
		avg_length: number;
		count: number;
	};

	const apiUrl = import.meta.env.VITE_API_DATA + '/summary/speech-lengths?group_by_party=true';

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
			legend: {
				display: false
			}
		},
		scales: {
			y: {
				beginAtZero: true,
				title: {
					display: true,
					text: 'Ord per anförande'
				}
			}
		}
	};

	onMount(async () => {
		try {
			const res = await fetch(apiUrl);
			if (!res.ok) throw new Error(`Fetch failed: ${res.status}`);
			const result: SpeechLengthItem[] = await res.json();

			chartData.labels = result.map((d) => d.party || 'Neutral');
			chartData.datasets[0].data = result
				.map((d) => d.avg_length)
				.filter((val): val is number => typeof val === 'number');

			chartData.datasets[0].backgroundColor = result.map((d) => getPartyColor(d.party));
		} catch (err) {
			console.error('Failed to fetch chart data:', err);
		}
	});
</script>

<Bar data={chartData} {options} />
