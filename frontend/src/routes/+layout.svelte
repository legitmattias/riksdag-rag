// src/routes/+layout.svelte
<script lang="ts">
  export let data;
</script>

<main class="min-h-screen bg-gray-50 text-gray-900">
  <header class="p-4 bg-white shadow">
    <h1 class="text-2xl font-bold">Riksdagsdata Dashboard</h1>
  </header>

  <section class="p-6">
    <slot />
  </section>
</main>