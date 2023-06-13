import { UserAgent } from '@algolia/autocomplete-shared';
import type { MultipleQueriesQuery, SearchForFacetValuesResponse, SearchResponse, SearchClient } from '../types';
export interface SearchParams {
    /**
     * The initialized Algolia search client.
     */
    searchClient: SearchClient;
    /**
     * A list of queries to execute.
     */
    queries: MultipleQueriesQuery[];
    /**
     * A list of user agents to add to the search client.
     *
     * This is useful to track usage of an integration.
     */
    userAgents?: UserAgent[];
}
export declare function fetchAlgoliaResults<TRecord>({ searchClient, queries, userAgents, }: SearchParams): Promise<Array<SearchResponse<TRecord> | SearchForFacetValuesResponse>>;
