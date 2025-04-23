<!-- src/components/TableControls.svelte -->
<script lang="ts">
    import { createEventDispatcher, onMount } from 'svelte';
  
    export let selectedParty: string = '';
    export let limit: number = 25;
    export let skip: number = 0;
  
    const dispatch = createEventDispatcher();
    let parties: { code: string; label: string }[] = [];
  
    async function fetchParties() {
      try {
        const res = await fetch(import.meta.env.VITE_API_META + '/parties');
        parties = await res.json();
      } catch (err) {
        console.error('Failed to fetch parties:', err);
      }
    }
  
    function applyFilters() {
      dispatch('update', { selectedParty, limit, skip });
    }
  
    function nextPage() {
      skip += limit;
      applyFilters();
    }
  
    function prevPage() {
      skip = Math.max(skip - limit, 0);
      applyFilters();
    }
  
    onMount(fetchParties);
  </script>
  
  <div class="mb-4 flex flex-wrap gap-4 items-end">
    <div>
        <label for="party-select" class="block text-sm font-medium text-gray-700">Parti</label>
        <select id="party-select" bind:value={selectedParty} on:change={applyFilters} class="mt-1 p-2 border rounded min-w-[13rem]">        
        <option value="">Alla</option>
        {#each parties as p}
          <option value={p.code}>{p.label}</option>
        {/each}
      </select>
    </div>
  
    <div>
        <label for="limit-select" class="block text-sm font-medium text-gray-700">Antal per sida</label>
        <select id="limit-select" bind:value={limit} on:change={applyFilters} class="mt-1 p-2 border rounded min-w-[4rem]">        
        <option value={10}>10</option>
        <option value={25}>25</option>
        <option value={50}>50</option>
      </select>
    </div>
  
    <div class="flex gap-2 mt-4">
      <button on:click={prevPage} class="px-3 py-1 bg-gray-200 rounded">Föregående</button>
      <button on:click={nextPage} class="px-3 py-1 bg-gray-200 rounded">Nästa</button>
    </div>
  </div>
  