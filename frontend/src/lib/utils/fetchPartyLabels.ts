// src/lib/utils/fetchPartyLabels.ts
export async function fetchPartyLabels() {
	const res = await fetch(import.meta.env.VITE_API_META + '/parties');
	const data = await res.json();
	const labelMap: Record<string, string> = {};

	for (const p of data) {
		labelMap[p.code] = p.label;
	}

	return labelMap;
}
