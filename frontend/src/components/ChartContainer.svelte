<script lang="ts">
	export let title: string;
</script>

<div class="flex flex-col items-center rounded bg-white p-4 shadow">
	<h3 class="mb-4 text-lg font-semibold">{title}</h3>
	<div class="w-full md:w-4/5">
		<slot />
	</div>
</div>
