<!-- src/routes/about/+page.svelte -->

<script lang="ts">
</script>

<section class="mx-auto max-w-4xl p-6">
	<h1 class="mb-6 text-2xl font-bold">Om applikationen</h1>

	<p class="mb-4">
		Den här applikationen låter dig utforska och söka bland anföranden från Sveriges riksdag på ett
		nytt sätt.
	</p>

	<ul class="mb-6 list-inside list-disc space-y-2">
		<li>Bläddra bland tusentals anföranden.</li>
		<li>Visualisera debattaktivitet över tid, per parti och talare.</li>
		<li>Sök med naturligt språk genom en inbyggd AI-assistent baserad på anförandena.</li>
	</ul>

	<p class="mb-6">
		Datasetet är baserat på officiella kammarprotokoll från 2022 till 2025, hämtade från <a
			href="https://www.riksdagen.se/sv/dokument-och-lagar/riksdagens-oppna-data/"
			>Riksdagens öppna dataportal</a
		>. Applikationen erbjuder både sammanfattningar och direktlänkar till de fullständiga
		protokollen.
	</p>

	<p class="mb-8 text-sm text-gray-600">
		Observera: Svaren från AI-assistenten baseras på utdrag från anföranden och speglar inte
		nödvändigtvis fullständiga politiska ståndpunkter.
	</p>

	<h2 class="mb-4 text-xl font-semibold">Teknik och utveckling</h2>

	<p class="mb-4">
		Frontend är byggd med SvelteKit och TailwindCSS för en snabb och responsiv användarupplevelse.
		Backend är baserad på FastAPI, för åtkomst till talardata och semantisk sökning.
	</p>

	<p class="mb-4">
		MongoDB och ChromaDB används för lagring av anföranden och AI-embeddings. Den semantiska
		sökningen kombinerar vektorbaserad återhämtning och språkmodellsgenerering för att möjliggöra
		flexibla frågor.
	</p>

	<p class="text-sm text-gray-600">
		Det här projektet har utvecklats inom ramen för en universitetskurs om webbteknologier och
		API-design.
	</p>
</section>
