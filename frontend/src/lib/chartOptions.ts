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
};

export function createBaseOptions({
	minimal = false,
	counts = [],
	unitLabel = '',
	axisLabel = 'Ord per anförande',
	datalabelPosition = 'inside',
	indexAxis = 'x'
}: OptionsArgs): ChartOptions<'bar'> {
	const plugins: ChartOptions<'bar'>['plugins'] = {
		legend: { display: false },
		tooltip: {
			callbacks: {
				label: function (context) {
					const partyMap = get(partyLabels) as Record<string, string>;
					const label = context.label;
					const fullLabel = partyMap[label] ?? label;
					const value = context.formattedValue;
					const count = counts?.[context.dataIndex];

					return `${fullLabel}: ${value} ${unitLabel}${count !== undefined ? ` (${count} anföranden)` : ''}`;
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
					formatter: (_value, context) => {
						const count = counts?.[context.dataIndex];
						return count ? `${count}` : '';
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
