import { SizingData } from './getSizingData';
export type CalculatedNodeHeights = number[];
export default function calculateNodeHeight(sizingData: SizingData, value: string, minRows?: number, maxRows?: number): CalculatedNodeHeights;
