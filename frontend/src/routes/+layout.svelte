<script lang="ts">
  // export let data;
  import '../app.css';
</script>

<div class="min-h-screen flex bg-gray-100 text-gray-900 font-sans">
  <!-- Sidebar -->
  <aside class="w-64 bg-white shadow-md hidden md:block">
    <div class="p-6 border-b">
      <h1 class="text-2xl font-bold">Riksdagsdata</h1>
    </div>
    <nav class="p-4 space-y-2">
      <a href="/dashboard" class="block py-2 px-4 rounded hover:bg-gray-100">Dashboard</a>
      <a href="/explore/speech-length" class="block py-2 px-4 rounded hover:bg-gray-100">Längd per anförande</a>
      <a href="/explore/speakers" class="block py-2 px-4 rounded hover:bg-gray-100">Aktiva talare</a>
      <a href="/explore/over-time" class="block py-2 px-4 rounded hover:bg-gray-100">Anföranden över tid</a>
    </nav>
  </aside>

  <!-- Main content -->
  <main class="flex-1 p-4 md:p-6">
    <div class="bg-blue-100 text-blue-800 p-4 rounded">This should be styled</div>
    <slot />
  </main>
</div>
