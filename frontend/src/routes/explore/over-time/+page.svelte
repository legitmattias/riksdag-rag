<!-- src/routes/explore/over-time/+page.svelte -->
<script lang="ts">
    import ChartContainer from '$components/ChartContainer.svelte';
    import SpeechesOverTimeChart from '$components/SpeechesOverTimeChart.svelte'
  </script>
  
  <ChartContainer title="Anföranden över tid">
    <SpeechesOverTimeChart />
  </ChartContainer>
  