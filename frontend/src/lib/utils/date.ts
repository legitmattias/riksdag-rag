// src/lib/utils/date.ts
export function formatDateSwedish(dateStr: string | undefined): string {
	if (!dateStr) return '';
	const date = new Date(dateStr);
	return date.toLocaleDateString('sv-SE', {
		year: 'numeric',
		month: 'long',
		day: 'numeric'
	});
}
