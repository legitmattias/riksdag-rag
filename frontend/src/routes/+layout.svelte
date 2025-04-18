<!-- src/routes/+layout.svelte -->
<script lang="ts">
	// export let data;
</script>

<main class="min-h-screen bg-gray-50 font-sans text-gray-900">
	<header class="mb-4 bg-white p-4 shadow">
		<div class="mx-auto flex max-w-7xl items-center justify-between">
			<h1 class="text-2xl font-bold">Riksdagsdata Dashboard</h1>
		</div>
	</header>

	<section class="mx-auto max-w-7xl px-4 md:px-8">
		<slot />
	</section>
</main>
