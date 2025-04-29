<script lang="ts">
	export let title: string;
	export let reduced = false;
</script>

<div class={`rounded bg-white p-4 shadow ${reduced ? 'w-[80%]' : 'w-full'}`}>
	<h3 class="mb-2 text-lg font-semibold">{title}</h3>
	<slot />
</div>
