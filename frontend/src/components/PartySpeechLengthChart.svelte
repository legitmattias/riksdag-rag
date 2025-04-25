<script lang="ts">
	import { Bar } from 'svelte-chartjs';
	import type { ChartData, ChartOptions } from 'chart.js';
	import ChartDataLabels from 'chartjs-plugin-datalabels';
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

	ChartJS.register(BarElement, CategoryScale, LinearScale, Tooltip, Legend, ChartDataLabels);

	type SpeechLengthItem = {
		party: string | null;
		avg_length: number;
		count: number;
	};

	let startDate: string = '';
	let endDate: string = '';
	let counts: number[] = [];

    export let minimal: boolean = false;


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
			legend: { display: false },
			tooltip: {
				callbacks: {
					label: function (context) {
						const label = context.label;
						const avg = context.formattedValue;
						const count = counts[context.dataIndex];
						return `${label}: ${avg} ord/anfr. (${count} anföranden)`;
					}
				}
			},
			datalabels: {
				anchor: 'end',
				align: 'end',
				formatter: (value, context) => {
					const count = counts[context.dataIndex];
					return count ? `${count} st` : '';
				},
				font: {
					weight: 'bold'
				},
				color: '#374151' // Tailwind's gray-700
			}
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

			counts = result.map((d) => d.count);
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

{#if !minimal}
  <ChartControls {startDate} {endDate} on:update={handleUpdate} />
{/if}

<Bar data={chartData} {options} />
