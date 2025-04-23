<!-- src/components/SpeechesOverTimeChart.svelte -->
<script lang="ts">
    import { Bar } from 'svelte-chartjs';
    import type { ChartData, ChartOptions } from 'chart.js';
    import { onMount } from 'svelte';
    import { Chart as ChartJS, BarElement, CategoryScale, LinearScale, Tooltip, Legend } from 'chart.js';
    import { getPartyColor } from '$lib/colors';
  
    ChartJS.register(BarElement, CategoryScale, LinearScale, Tooltip, Legend);
  
    type TimeItem = {
      year: string;
      month?: string;
      party: string | null;
      count: number;
    };
  
    const apiUrl = import.meta.env.VITE_API_DATA + '/summary/speeches-over-time?group_by_party=true&resolution=year';
  
    let chartData: ChartData<'bar', number[], string> = {
      labels: [],
      datasets: []
    };
  
    const options: ChartOptions<'bar'> = {
      responsive: true,
      plugins: {
        legend: { display: true },
      },
      scales: {
        y: {
          beginAtZero: true,
          title: { display: true, text: 'Antal anföranden' }
        }
      }
    };
  
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
  
        chartData.datasets = Object.entries(grouped).map(([party, values]) => {
          return {
            label: party,
            backgroundColor: getPartyColor(party),
            data: sortedYears.map((year) => values[year] ?? 0)
          };
        });
      } catch (err) {
        console.error('Failed to fetch over-time chart data:', err);
      }
    });
  </script>
  
  <Bar data={chartData} {options} />
  