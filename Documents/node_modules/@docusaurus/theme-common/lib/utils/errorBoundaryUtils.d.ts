/**
 * Copyright (c) Facebook, Inc. and its affiliates.
 *
 * This source code is licensed under the MIT license found in the
 * LICENSE file in the root directory of this source tree.
 */
import React, { type ComponentProps } from 'react';
export declare function ErrorBoundaryTryAgainButton(props: ComponentProps<'button'>): JSX.Element;
export declare function ErrorBoundaryError({ error }: {
    error: Error;
}): JSX.Element;
/**
 * This component is useful to wrap a low-level error into a more meaningful
 * error with extra context, using the ES error-cause feature.
 *
 * <ErrorCauseBoundary
 *   onError={(error) => new Error("extra context message",{cause: error})}
 * >
 *   <RiskyComponent>
 * </ErrorCauseBoundary>
 */
export declare class ErrorCauseBoundary extends React.Component<{
    children: React.ReactNode;
    onError: (error: Error, errorInfo: React.ErrorInfo) => Error;
}, unknown> {
    componentDidCatch(error: Error, errorInfo: React.ErrorInfo): never;
    render(): React.ReactNode;
}
//# sourceMappingURL=errorBoundaryUtils.d.ts.map