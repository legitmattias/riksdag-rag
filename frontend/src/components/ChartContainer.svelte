<script lang="ts">
	export let title: string;
</script>

<div class="rounded bg-white p-4 shadow flex flex-col items-center">
	<h3 class="mb-4 text-lg font-semibold">{title}</h3>
	<div class="w-full md:w-4/5">
		<slot />
	</div>
</div>
