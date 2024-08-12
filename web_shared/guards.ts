import { ok as assert } from "assert";

export function assertNotNull<T>(
  arg: T,
): asserts arg is Exclude<T, null | undefined> {
  assert(arg !== null, "Invalid null");
}

export function assertNotUndefined<T>(
  arg: T,
): asserts arg is Exclude<T, undefined> {
  assert(arg !== undefined, "Invalid undefined");
}

export function assertNotNullNotUndefined<T>(
  arg: T,
): asserts arg is Exclude<T, null | undefined> {
  assertNotNull(arg);
  assertNotUndefined(arg);
}
