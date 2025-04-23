<!-- src/components/TopSpeakersChart.svelte -->
<script lang="ts">
    import { Bar } from 'svelte-chartjs';
    import type { ChartData, ChartOptions } from 'chart.js';
    import { onMount } from 'svelte';
    import { Chart as ChartJS, BarElement, CategoryScale, LinearScale, Tooltip, Legend } from 'chart.js';
  
    ChartJS.register(BarElement, CategoryScale, LinearScale, Tooltip, Legend);
  
    type SpeakerItem = {
      speaker: string;
      party: string | null
      count: number;
    };
  
    export let limit = 25;
    const apiUrl = `${import.meta.env.VITE_API_META}/top-speakers?limit=${limit}`;
  
    let chartData: ChartData<'bar', number[], string> = {
      labels: [],
      datasets: [
        {
          label: 'Antal anföranden',
          data: [],
          backgroundColor: 'rgba(34, 197, 94, 0.6)' // green
        }
      ]
    };
  
    const options: ChartOptions<'bar'> = {
      responsive: true,
      plugins: {
        legend: {
          display: false
        }
      },
      indexAxis: 'y',
      scales: {
        x: {
          beginAtZero: true,
          title: {
            display: true,
            text: 'Antal anföranden'
          }
        }
      }
    };
  
    onMount(async () => {
      try {
        const res = await fetch(apiUrl);
        if (!res.ok) throw new Error(`Fetch failed: ${res.status}`);
        const result: SpeakerItem[] = await res.json();
        chartData.labels = result.map((d) =>
            d.party ? `${d.speaker} (${d.party})` : d.speaker
        );
        chartData.datasets[0].data = result.map((d) => d.count);
      } catch (err) {
        console.error('Failed to fetch top speakers chart data:', err);
      }
    });
  </script>
  
  <Bar data={chartData} {options} />
  