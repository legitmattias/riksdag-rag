<!-- src/routes/rag/+page.svelte -->

<script lang="ts">
	import { writable } from 'svelte/store';

	const query = writable('');
	const answer = writable('');
	const sources = writable<SourceDocument[]>([]);
	const loading = writable(false);
	const error = writable('');

	type SourceDocument = {
		text: string;
		speaker?: string;
		party?: string;
		date?: string;
	};

	async function search() {
		loading.set(true);
		answer.set('');
		sources.set([]);
		error.set('');

		try {
			const baseUrl = import.meta.env.VITE_API_RAG;
			const res = await fetch(`${baseUrl}/rag/query`, {
				method: 'POST',
				headers: { 'Content-Type': 'application/json' },
				body: JSON.stringify({ query: $query })
			});

			if (!res.ok) {
				throw new Error(`Server error: ${res.status}`);
			}

			const data = await res.json();
			answer.set(data.answer);
			sources.set(data.sources);
		} catch (err) {
			if (err instanceof Error) {
				error.set(err.message);
			} else {
				error.set('An unknown error occurred.');
			}
		} finally {
			loading.set(false);
		}
	}
</script>

<section class="mx-auto max-w-4xl p-6">
	<h1 class="mb-6 text-2xl font-bold">Fråga riksdagsboten 🤖</h1>
	<p class="mb-2 text-sm text-gray-500">
		Observera att svaret baseras på ett urval av anföranden från riksdagens kammare och inte
		nödvändigtvis representerar en fullständig bild av partiets eller personens ståndpunkt.
	</p>

	<div class="mb-6 flex gap-4">
		<input
			type="text"
			placeholder="Skriv din fråga..."
			class="flex-1 rounded-lg border border-gray-300 px-4 py-2 focus:outline-none focus:ring-2 focus:ring-blue-500"
			bind:value={$query}
			on:keydown={(e) => e.key === 'Enter' && search()}
		/>
		<button
			class="rounded-lg bg-blue-600 px-6 py-2 text-white transition hover:bg-blue-700"
			on:click={search}
			disabled={$loading}
		>
			{$loading ? 'Söker...' : 'Sök'}
		</button>
	</div>

	{#if $error}
		<p class="mb-4 text-red-500">Fel: {$error}</p>
	{/if}

	{#if $answer}
		<div class="mb-8 rounded-lg bg-gray-100 p-4">
			<h2 class="mb-2 text-xl font-semibold">Svar:</h2>
			<p>{$answer}</p>
		</div>
	{/if}

	{#if $sources.length > 0}
		<div>
			<h2 class="mb-4 text-xl font-semibold">Källor:</h2>
			<div class="space-y-4">
				{#each $sources as source}
					<div class="rounded-lg bg-white p-4 shadow">
						<div class="mb-1 text-sm text-gray-500">
							{source.speaker} ({source.party}) — {source.date}
						</div>
						<p class="text-gray-700">{source.text}</p>
					</div>
				{/each}
			</div>
		</div>
	{/if}
</section>
