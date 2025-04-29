<!-- src/routes/about/+page.svelte -->

<script lang="ts">
</script>

<div class="rounded bg-white p-6 shadow">
	<h1 class="mb-4 text-2xl font-bold">Om projektet</h1>

	<p class="mb-4">
		Den här webbapplikationen låter dig utforska och analysera anföranden från svenska riksdagen
		(2022–2025). Projektet kombinerar interaktiv visualisering, filtrering, och semantisk sökning
		(RAG) på verklig data.
	</p>

	<p class="mb-4">Du kan:</p>
	<ul class="mb-4 list-disc pl-6">
		<li>Filtrera och analysera över 33 000 riksdagsanföranden.</li>
		<li>Utforska statistik om partier och talare.</li>
		<li>Ställa frågor med hjälp av en RAG-baserad sökfunktion (Riksdagsboten 🤖).</li>
	</ul>

	<p class="mb-4">
		Applikationen är baserad på öppna data från Riksdagen och utvecklad som en del av kursen 1DV027
		(Webbteknologier och API-design) vid Linnéuniversitetet.
	</p>

	<p class="text-sm text-gray-500">
		Rådata är hämtad från <a
			href="https://www.riksdagen.se/sv/dokument-och-lagar/riksdagens-oppna-data/dokument/"
			target="_blank"
			class="text-blue-600 hover:underline"
		>
			Riksdagens öppna data
		</a>.
	</p>
</div>
