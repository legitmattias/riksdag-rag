// src/lib/chartOptions.ts
import type { ChartOptions } from 'chart.js';

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
					const value = context.formattedValue;
					return `${value} ${unitLabel}`;
				}
			}
		},
		datalabels: minimal
			? {
					display: false // Disable in minimal mode (dashboard)
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
