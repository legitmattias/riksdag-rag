<!-- src/routes/explore/summaries/+page.svelte -->
<script lang="ts">
	import ChartContainer from '$components/ChartContainer.svelte';
	import SpeechSummaryTable from '$components/SpeechSummaryTable.svelte';
</script>

<ChartContainer title="Anförandeöversikt">
	<SpeechSummaryTable />
</ChartContainer>
