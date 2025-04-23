<!-- src/routes/explore/speech-length/+page.svelte -->
<script lang="ts">
    import ChartContainer from '$components/ChartContainer.svelte';
    import PartySpeechLengthChart from '$components/PartySpeechLengthChart.svelte';
  </script>
  
  <ChartContainer title="Längd på anföranden per parti">
    <PartySpeechLengthChart />
  </ChartContainer>
  