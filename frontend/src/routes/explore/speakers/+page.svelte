<!-- src/routes/explore/speakers/+page.svelte -->
<script lang="ts">
    import ChartContainer from '$components/ChartContainer.svelte';
    import TopSpeakersChart from '$components/TopSpeakersChart.svelte';
  </script>
  
  <ChartContainer title="Mest aktiva talare (anföranden)">
    <TopSpeakersChart />
  </ChartContainer>
