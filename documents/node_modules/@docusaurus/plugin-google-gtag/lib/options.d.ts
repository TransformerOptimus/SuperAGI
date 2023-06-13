import type { OptionValidationContext, ThemeConfig, ThemeConfigValidationContext } from '@docusaurus/types';
export declare type PluginOptions = {
    trackingID: [string, ...string[]];
    anonymizeIP: boolean;
};
export declare type Options = {
    trackingID: string | [string, ...string[]];
    anonymizeIP?: boolean;
};
export declare const DEFAULT_OPTIONS: Partial<PluginOptions>;
export declare function validateOptions({ validate, options, }: OptionValidationContext<Options, PluginOptions>): PluginOptions;
export declare function validateThemeConfig({ themeConfig, }: ThemeConfigValidationContext<ThemeConfig>): ThemeConfig;
