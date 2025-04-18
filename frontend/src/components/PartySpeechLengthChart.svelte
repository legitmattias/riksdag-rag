<!-- src/components/PartySpeechLengthChart.svelte -->
<script lang="ts">
	import { Bar } from 'svelte-chartjs';
	import type { ChartData, ChartOptions } from 'chart.js';
	import { onMount } from 'svelte';

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
				backgroundColor: 'rgba(59, 130, 246, 0.6)'
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
		const res = await fetch(apiUrl);
		const result: SpeechLengthItem[] = await res.json();

		chartData.labels = result.map((d) => d.party || 'Neutral');
		chartData.datasets[0].data = result
			.map((d) => d.avg_length)
			.filter((val): val is number => typeof val === 'number');
	});
</script>

<Bar data={chartData} {options} />
