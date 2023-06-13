/**
 * Detect when an event is modified with a special key to let the browser
 * trigger its default behavior.
 */
export declare function isModifierEvent<TEvent extends KeyboardEvent | MouseEvent>(event: TEvent): boolean;
