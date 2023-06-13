import { Loader } from './index';
import { Cache, CosmiconfigResult, ExplorerOptions, ExplorerOptionsSync, LoadedFileContent } from './types';
declare class ExplorerBase<T extends ExplorerOptions | ExplorerOptionsSync> {
    protected readonly loadCache?: Cache;
    protected readonly searchCache?: Cache;
    protected readonly config: T;
    constructor(options: T);
    clearLoadCache(): void;
    clearSearchCache(): void;
    clearCaches(): void;
    private validateConfig;
    protected shouldSearchStopWithResult(result: CosmiconfigResult): boolean;
    protected nextDirectoryToSearch(currentDir: string, currentResult: CosmiconfigResult): string | null;
    private loadPackageProp;
    protected getLoaderEntryForFile(filepath: string): Loader;
    protected loadedContentToCosmiconfigResult(filepath: string, loadedContent: LoadedFileContent, forceProp: boolean): CosmiconfigResult;
    protected validateFilePath(filepath: string): void;
}
declare function getExtensionDescription(filepath: string): string;
export { ExplorerBase, getExtensionDescription };
//# sourceMappingURL=ExplorerBase.d.ts.map