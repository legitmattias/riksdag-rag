<script lang="ts">
	// export let data;
	import '../app.css';
</script>

<div class="flex min-h-screen bg-gray-100 font-sans text-gray-900">
	<!-- Sidebar -->
	<aside class="hidden w-64 bg-white shadow-md md:block">
		<div class="border-b p-6">
			<h1 class="text-2xl font-bold">Riksdagsdata</h1>
		</div>
		<nav class="space-y-2 p-4">
			<a href="/dashboard" class="block rounded px-4 py-2 hover:bg-gray-100">Översikt</a>
			<a href="/rag" class="block rounded px-4 py-2 hover:bg-gray-100">🤖 Riksdagsboten (RAG)</a>
			<a href="/explore/speech-length" class="block rounded px-4 py-2 hover:bg-gray-100"
				>Längd per anförande</a
			>
			<a href="/explore/speakers" class="block rounded px-4 py-2 hover:bg-gray-100">Aktiva talare</a
			>
			<a href="/explore/over-time" class="block rounded px-4 py-2 hover:bg-gray-100"
				>Anföranden över tid</a
			>
			<a href="/explore/summaries" class="block rounded px-4 py-2 hover:bg-gray-100"
				>Översikt över anföranden</a
			>
		</nav>
	</aside>

	<!-- Main content -->
	<main class="flex-1 p-4 md:p-6">
		<div class="rounded bg-blue-100 p-4 text-blue-800">This should be styled</div>
		<slot />
	</main>
</div>
