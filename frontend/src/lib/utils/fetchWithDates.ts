// src/lib/utils/fetchWithDates.ts
export async function fetchWithDates(baseUrl: string, startDate?: string, endDate?: string) {
	const url = new URL(baseUrl);
	if (startDate) url.searchParams.set('start_date', startDate);
	if (endDate) url.searchParams.set('end_date', endDate);

	const res = await fetch(url.toString());
	if (!res.ok) throw new Error(`Fetch failed: ${res.status}`);
	return res.json();
}
