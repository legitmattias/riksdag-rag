// src/lib/chartOptions.ts
import type { ChartOptions } from 'chart.js';
import { get } from 'svelte/store';
import { partyLabels } from '$lib/stores/partyStore';

type OptionsArgs = {
	minimal?: boolean;
	counts?: number[];
	unitLabel?: string;
	axisLabel?: string;
	datalabelPosition?: 'inside' | 'above';
	indexAxis?: 'x' | 'y';
	showTooltipCount?: boolean;
	showPartyCode?: boolean;
};

export function createBaseOptions({
	minimal = false,
	counts = [],
	unitLabel = '',
	axisLabel = 'Ord per anförande',
	datalabelPosition = 'inside',
	indexAxis = 'x',
	showTooltipCount = true,
	showPartyCode = false
}: OptionsArgs): ChartOptions<'bar'> {
	const plugins: ChartOptions<'bar'>['plugins'] = {
		legend: { display: false },
		tooltip: {
			callbacks: {
				label: function (context) {
					const partyMap = get(partyLabels) as Record<string, string>;

					// Use dataset label (party code), not x-axis label (year)
					const datasetLabel = context.dataset.label as string;
					const fullPartyName = partyMap[datasetLabel] ?? datasetLabel;

					let labelToShow = fullPartyName;
					if (showPartyCode && fullPartyName !== datasetLabel) {
						labelToShow = `${fullPartyName} (${datasetLabel})`;
					}

					const value = context.formattedValue;
					const count = counts?.[context.dataIndex];

					const base = `${labelToShow}: ${value} ${unitLabel}`;
					if (showTooltipCount && count !== undefined && count !== Number(value)) {
						return `${base} (${count} anföranden)`;
					}
					return base;
				},
				title: function () {
					// Disable default title
					return '';
				}
			}
		},
		datalabels: minimal
			? {
					display: false // Disable in minimal (dashboard) mode
				}
			: {
					anchor: datalabelPosition === 'above' ? 'end' : 'center',
					align: datalabelPosition === 'above' ? 'end' : 'center',
					formatter: (value, context) => {
						if (counts?.length) {
							const count = counts[context.dataIndex];
							return count ? `${count}` : '';
						}
						return `${Math.round(Number(value))}`; // fallback: show bar value itself
					},
					font: { weight: 'bold' },
					color: '#374151'
				}
	};

	return {
		responsive: true,
		indexAxis,
		plugins,
		scales: {
			y: {
				beginAtZero: true,
				title: { display: indexAxis === 'x', text: axisLabel }
			},
			x: {
				beginAtZero: true,
				title: { display: indexAxis === 'y', text: axisLabel }
			}
		}
	};
}
