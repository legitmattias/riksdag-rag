<script lang="ts">
  export let title: string;
</script>

<div class="p-4 bg-white shadow rounded">
  <h3 class="text-lg font-semibold mb-2">{title}</h3>
  <slot />
</div>