<!-- src/routes/+layout.svelte -->
<script lang="ts">
    export let data;
</script>

<main class="min-h-screen bg-gray-50 text-gray-900 font-sans">
<header class="p-4 bg-white shadow mb-4">
    <div class="max-w-7xl mx-auto flex items-center justify-between">
    <h1 class="text-2xl font-bold">Riksdagsdata Dashboard</h1>
    </div>
</header>

<section class="px-4 md:px-8 max-w-7xl mx-auto">
    <slot />
</section>
</main>
