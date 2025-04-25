// src/lib/stores/partyStore.ts
import { browser } from '$app/environment';
import { writable } from 'svelte/store';
import { fetchPartyLabels } from '$lib/utils/fetchPartyLabels';

function createPartyStore() {
	const { subscribe, set } = writable<Record<string, string>>({});

	let initialized = false;

	return {
		subscribe(run: (value: Record<string, string>) => void) {
			if (browser && !initialized) {
				initialized = true;
				fetchPartyLabels().then((labels) => {
					set(labels);
				});
			}
			return subscribe(run);
		}
	};
}

export const partyLabels = createPartyStore();
