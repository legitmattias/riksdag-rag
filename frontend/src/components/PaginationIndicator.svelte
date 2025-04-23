<!-- src/components/PaginationIndicator.svelte -->
<script lang="ts">
    export let skip: number = 0;
    export let limit: number = 25;
  
    $: currentPage = Math.floor(skip / limit) + 1;
  </script>
  
  <p class="text-sm text-gray-500 mb-2">Sida {currentPage}</p>
  