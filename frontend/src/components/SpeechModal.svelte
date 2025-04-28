<!-- src/components/SpeechModal.svelte -->
<script lang="ts">
	import { onMount } from 'svelte';
	import { writable } from 'svelte/store';

	export let speechId: string;
	export let onClose: () => void;

	const loading = writable(true);
	const speech = writable<any>(null);
	const error = writable('');

	async function fetchSpeech() {
		try {
			const res = await fetch(`${import.meta.env.VITE_API_DATA}/speeches/${speechId}`);
			if (!res.ok) {
				throw new Error(`Serverfel: ${res.status}`);
			}
			const data = await res.json();
			speech.set(data);
		} catch (err) {
			if (err instanceof Error) {
				error.set(err.message);
			} else {
				error.set('Ett okänt fel inträffade.');
			}
		} finally {
			loading.set(false);
		}
	}

	onMount(() => {
		fetchSpeech();
	});
</script>

<div class="fixed inset-0 z-50 flex items-center justify-center bg-black bg-opacity-50">
	<div class="relative max-h-[90vh] w-full max-w-3xl overflow-y-auto rounded-lg bg-white p-6">
		<button class="absolute right-4 top-4 text-gray-500 hover:text-gray-800" on:click={onClose}>
			✖
		</button>

		{#if $loading}
			<p class="text-center">Laddar anförande...</p>
		{:else if $error}
			<p class="text-center text-red-500">Fel: {$error}</p>
		{:else if $speech}
			<div class="space-y-4">
				<div class="text-sm text-gray-700">
					<strong>{$speech.speaker}</strong> ({$speech.party}) — {$speech.date}
				</div>

				<div class="prose max-w-none">
					{@html $speech.text.replace(/\n/g, '<br>')}
				</div>

				<div class="mt-6 space-x-4">
					{#if $speech.source?.html}
						<a
							href={$speech.source.html}
							target="_blank"
							class="inline-block rounded bg-blue-600 px-4 py-2 text-white transition hover:bg-blue-700"
						>
							Visa protokoll (HTML)
						</a>
					{/if}
					{#if $speech.source?.pdf?.url}
						<a
							href={$speech.source.pdf.url}
							target="_blank"
							class="inline-block rounded bg-green-600 px-4 py-2 text-white transition hover:bg-green-700"
						>
							Ladda ned protokoll (PDF)
						</a>
					{/if}
				</div>
			</div>
		{/if}
	</div>
</div>
