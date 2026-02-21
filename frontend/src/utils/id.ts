export function createLocalId() {
  return `${Date.now()}-${Math.random().toString(16).slice(2)}`;
}
