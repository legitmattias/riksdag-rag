<script lang="ts">
	export let title: string;
</script>

<div class="rounded bg-white p-4 shadow">
	<h3 class="mb-2 text-lg font-semibold">{title}</h3>
	<slot />
</div>
