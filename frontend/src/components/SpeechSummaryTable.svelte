<!-- src/components/SpeechSummaryTable.svelte -->
<script lang="ts">
    import { onMount } from 'svelte';
  
    type SpeechSummary = {
      speaker: string;
      party?: string;
      date: string;
      clause_title: string;
      speech_number: number;
      length?: number;
    };
  
    const apiUrl = import.meta.env.VITE_API_DATA + '/speeches/summary?limit=50';
    let summaries: SpeechSummary[] = [];
    let isLoading = true;
  
    onMount(async () => {
      try {
        const res = await fetch(apiUrl);
        if (!res.ok) throw new Error(`Fetch failed: ${res.status}`);
        summaries = await res.json();
      } catch (err) {
        console.error('Failed to fetch summaries:', err);
      } finally {
        isLoading = false;
      }
    });
  </script>
  
  {#if isLoading}
    <p class="text-sm text-gray-500">Laddar anforanden...</p>
  {:else}
    <div class="overflow-auto">
      <table class="min-w-full text-sm border">
        <thead class="bg-gray-100 text-left">
          <tr>
            <th class="px-4 py-2">Talare</th>
            <th class="px-4 py-2">Parti</th>
            <th class="px-4 py-2">Datum</th>
            <th class="px-4 py-2">Rubrik</th>
            <th class="px-4 py-2">Ord</th>
          </tr>
        </thead>
        <tbody>
          {#each summaries as s}
            <tr class="border-t hover:bg-gray-50">
              <td class="px-4 py-2 font-medium">{s.speaker}</td>
              <td class="px-4 py-2">{s.party || '–'}</td>
              <td class="px-4 py-2">{s.date}</td>
              <td class="px-4 py-2">{s.clause_title}</td>
              <td class="px-4 py-2">{s.length ?? '–'}</td>
            </tr>
          {/each}
        </tbody>
      </table>
    </div>
  {/if}
  