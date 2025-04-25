<script lang="ts">
	import ChartContainer from '$components/ChartContainer.svelte';
	import PartySpeechLengthChart from '$components/PartySpeechLengthChart.svelte';
	import TopSpeakersChart from '$components/TopSpeakersChart.svelte';
	import SpeechesOverTimeChart from '$components/SpeechesOverTimeChart.svelte';
</script>

<h2 class="mb-4 text-xl font-semibold">Översikt</h2>

<div class="grid gap-6 sm:grid-cols-2 xl:grid-cols-3">
	<ChartContainer title="Längd på anföranden per parti">
		<PartySpeechLengthChart minimal={true} />
	</ChartContainer>

	<ChartContainer title="Mest aktiva talare (anföranden)">
		<TopSpeakersChart limit={10} />
	</ChartContainer>

	<ChartContainer title="Anföranden per år">
		<SpeechesOverTimeChart />
	</ChartContainer>
</div>
