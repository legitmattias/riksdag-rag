<!-- src/components/PaginationIndicator.svelte -->
<script lang="ts">
	export let skip: number = 0;
	export let limit: number = 25;
	export let total: number = 0;

	$: currentPage = Math.floor(skip / limit) + 1;
	$: maxPage = Math.ceil(total / limit);
	$: currentCount = Math.min(skip + limit, total);
</script>

<p class="mb-2 text-sm text-gray-500">
	Sida {currentPage} av {maxPage} ({currentCount} / {total} anföranden)
</p>
