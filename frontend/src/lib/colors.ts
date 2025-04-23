// src/lib/colors.ts
export const partyColors: Record<string, string> = {
	S: '#e30613',
	M: '#52bdec',
	V: '#af1916',
	C: '#00a886',
	L: '#002a8d',
	KD: '#193a83',
	MP: '#83cf39',
	SD: '#ffcc00',
	'': '#9ca3af',
	UNKNOWN: '#d1d5db'
};

export function getPartyColor(party: string | null | undefined): string {
	return partyColors[party || ''] ?? partyColors.UNKNOWN;
}
