/**
 * Common CSS class patterns used throughout the application
 */

export const commonStyles = {
  card: "shadow-none",
  cardWithBorder: "p-4 border rounded-lg bg-white shadow-none",
  cardTransition: "transition-colors rounded-lg shadow-none border",
  formElement: "shadow-none",
  tabTrigger: "flex items-center gap-2 rounded-xl p-6 border-none data-[state=active]:shadow-none shadow-none",
} as const;

export function cn(...classes: (string | undefined)[]): string {
  return classes.filter(Boolean).join(" ");
}