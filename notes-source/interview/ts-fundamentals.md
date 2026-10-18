**61. What is the difference between `any` and `unknown`? When should you use each?**

<details>
<summary>Answer</summary>

Both accept any value. `any` switches type checking **off**: you can do anything with it. `unknown` is the **type-safe** top type: you can't use it until you narrow it. Default to `unknown` for values you don't know the shape of (API responses, `JSON.parse`, `catch` errors). Use `any` only as a temporary escape hatch, e.g. while migrating JS code.

| | `any` | `unknown` |
|---|---|---|
| Assign any value to it | ✅ | ✅ |
| Assign it to other types | ✅ (unchecked) | ❌ only to `unknown`/`any` |
| Access props / call it | ✅ (unchecked) | ❌ until narrowed |
| Spreads to other code | Yes, silently | No |

```ts
let a: any = "hello";
a.toFixed(2); // compiles, but crashes at runtime: TypeError: a.toFixed is not a function

let u: unknown = JSON.parse('{"name":"Ritesh"}');
// u.name;    // ❌ Error: 'u' is of type 'unknown'.
if (typeof u === "object" && u !== null && "name" in u) {
  console.log(u.name); // Ritesh
}
```

- **Follow-up:** with `strict` (`useUnknownInCatchVariables`), `catch (e)` gives `e` the type `unknown`, so you narrow it with `e instanceof Error` before reading `e.message`.
- **Pitfall:** `any` spreads. A value you read from an `any` is also `any`, so type safety quietly disappears in the code that uses it. For real payloads, validate with a schema library (zod, class-validator) instead of casting.

</details>

**62. What is the difference between `void` and `never` return types?**

<details>
<summary>Answer</summary>

`void` means the function **returns normally but gives back nothing useful** (it returns `undefined`). `never` means the function **never returns at all**: it always throws, or it loops forever.

| | `void` | `never` |
|---|---|---|
| Function completes? | Yes | No (throws / infinite loop) |
| Typical use | Loggers, event handlers | Error helpers, exhaustive checks |
| Assignable to other types | No | Yes (it's the bottom type) |

```ts
function log(msg: string): void {
  console.log(msg);
}

function fail(msg: string): never {
  throw new Error(msg);
}

// Exhaustiveness check with never
type Status = "active" | "blocked";
function label(s: Status): string {
  switch (s) {
    case "active": return "Active";
    case "blocked": return "Blocked";
    default: return assertNever(s); // compile error if a new Status is added but not handled
  }
}
function assertNever(x: never): never {
  throw new Error("Unexpected value: " + x);
}
console.log(label("blocked")); // Blocked
```

- **Pitfall:** a callback typed as returning `void` may still return a value. `const cb: (n: number) => void = (n) => arr.push(n)` compiles even though `push` returns a number. The caller just promises to ignore it. This is why `forEach(x => arr.push(x))` is allowed.
- **Follow-up:** `never` is also what you get after narrowing removes every case, and from impossible intersections like `string & number`.

</details>

**63. What is a Tuple type? How is it different from an array type?**

<details>
<summary>Answer</summary>

A tuple is a **fixed-length array where each position has its own type**, e.g. `[string, number]`. A normal array type like `number[]` has any length, and every element has the same type.

| | Array `T[]` | Tuple `[A, B]` |
|---|---|---|
| Length | Any | Fixed (can have optional/rest parts) |
| Element types | All the same | Set per position |
| Example | `string[]` | `[name: string, age: number]` |

```ts
let user: [string, number] = ["Ritesh", 25];
// user = [25, "Ritesh"]; // ❌ Error: Type 'number' is not assignable to type 'string'.

const [name, age] = user;
console.log(name, age); // Ritesh 25

type Point = readonly [x: number, y: number]; // labelled + readonly
type WithOptional = [string, number?];
type WithRest = [string, ...number[]];

// Real-world: React's useState returns a tuple
function useCounter(): [number, (n: number) => void] {
  let c = 0;
  return [c, (n) => { c = n; }];
}
```

- **Pitfall:** mutable tuples still let you call `push`. `user.push(99)` compiles and breaks the fixed length. Use `readonly [string, number]` or `as const` to stop that.
- **Follow-up:** return a tuple when callers will rename the values on destructuring (like `useState`). Return an object when there are more than 2–3 values.

</details>

**64. What is the difference between an `interface` and a `type alias`? When would you prefer each?**

<details>
<summary>Answer</summary>

Both can describe object shapes, and in most code you can use either one. The key differences: **interfaces can be reopened (declaration merging) and extended with `extends`**. **Type aliases can name any type**: unions, tuples, primitives, mapped and conditional types.

| Feature | `interface` | `type` |
|---|---|---|
| Object shapes | ✅ | ✅ |
| Unions / tuples / primitives | ❌ | ✅ |
| Mapped / conditional types | ❌ | ✅ |
| Declaration merging | ✅ | ❌ (duplicate identifier error) |
| Extending | `extends` (catches conflicts) | `&` intersection (conflicts become `never`) |
| `implements` in a class | ✅ | ✅ (only for object types) |

```ts
interface User { id: number; name: string }
interface Admin extends User { permissions: string[] }

type ID = string | number;                      // only a type alias can do this
type ApiState = "idle" | "loading" | "error";
type Point = [number, number];
type AdminT = User & { permissions: string[] }; // intersection
```

**When to prefer each:**
- `interface` for object contracts and public/library APIs that others may extend, e.g. NestJS DTO shapes and class contracts. Its error messages are also clearer, and the compiler caches extended interfaces better.
- `type` for unions, discriminated unions, function types, tuples and utility/mapped types.
- Most important: **be consistent** within the codebase.

- **Pitfall:** with `extends`, a conflicting property type is a compile error at the declaration. With `&`, the conflicting property silently becomes `never`.

</details>

**65. What is declaration merging in TypeScript? When is it useful?**

<details>
<summary>Answer</summary>

Declaration merging is when the compiler **combines several declarations with the same name into one definition**. The most common case: two `interface` declarations with the same name merge their members. Namespaces merge too, and so do namespaces with classes, functions or enums.

```ts
interface User { name: string }
interface User { age: number }

const u: User = { name: "Ritesh", age: 25 }; // must have both
```

**When it's useful: augmenting third-party types** without forking them.

```ts
// types/express.d.ts: add `user` to Express's Request (e.g. set by an auth guard/middleware)
declare global {
  namespace Express {
    interface Request {
      user?: { id: string; role: string };
    }
  }
}
export {};
```

Other uses: adding properties to `Window` (for example `window.dataLayer`), extending a library's theme type (MUI, styled-components), and adding custom matchers to Jest's `Matchers`.

- **Pitfall:** `type` aliases **don't** merge. Declaring `type User` twice gives "Duplicate identifier". If two merged interfaces declare the same property with different types, that's an error.
- **Pitfall:** because merging is global, a library interface can be extended by accident from anywhere. That's one reason some teams prefer `type` for internal models.

</details>

**66. What is `readonly` and how is it different from `const`?**

<details>
<summary>Answer</summary>

`const` works on **variables**: the binding can't be reassigned, but the object it points to can still change. `readonly` works on **properties, arrays and tuples** at the type level: the property can't be reassigned through that type. Both checks are **shallow**, and `readonly` exists only at compile time.

| | `const` | `readonly` |
|---|---|---|
| Applies to | Variable bindings | Properties, index signatures, arrays/tuples |
| Checked at | Compile time + runtime (JS) | Compile time only |
| Stops mutating contents? | ❌ | ✅ (one level deep) |

```ts
const arr = [1, 2];
arr.push(3);   // ✅ allowed: const only locks the binding
// arr = [];   // ❌ Error: Cannot assign to 'arr' because it is a constant.

interface Config { readonly apiUrl: string }
const c: Config = { apiUrl: "/api" };
// c.apiUrl = "/v2"; // ❌ Error: Cannot assign to 'apiUrl' because it is a read-only property.

const nums: readonly number[] = [1, 2];
// nums.push(3);  // ❌ Error: Property 'push' does not exist on type 'readonly number[]'.

const cfg = { apiUrl: "/api", retries: 3 } as const;
// type: { readonly apiUrl: "/api"; readonly retries: 3 }
```

- **Pitfall:** `readonly` is shallow, so `readonly user: { name: string }` still allows `obj.user.name = "x"`. For runtime immutability use `Object.freeze` (also shallow). For deep compile-time immutability use a `DeepReadonly` mapped type.
- **Follow-up:** in a class, `constructor(private readonly repo: UserRepo)` (a common NestJS pattern) stops anyone from reassigning the injected dependency.

</details>

**67. What is a union type? What is a discriminated union and why is it useful?**

<details>
<summary>Answer</summary>

A **union** `A | B` means a value can be *one of* several types. Before you can use members that only some of the types have, you must narrow it with `typeof`, `in`, `instanceof` or an equality check. A **discriminated union** is a union of object types that share a **literal "tag" property** (such as `kind` or `status`). Checking that tag narrows the value to exactly one type, and the compiler can check that you handled every case.

```ts
type Id = string | number; // simple union

type Shape =
  | { kind: "circle"; radius: number }
  | { kind: "square"; side: number };

function area(s: Shape): number {
  switch (s.kind) {
    case "circle": return Math.PI * s.radius ** 2; // s is narrowed to circle
    case "square": return s.side ** 2;
    default: {
      const _exhaustive: never = s; // errors if a new Shape is added and not handled
      return _exhaustive;
    }
  }
}
console.log(area({ kind: "square", side: 3 })); // 9
```

**Why it's useful:** it rules out impossible states. A typical React/API example:

```ts
type RequestState<T> =
  | { status: "loading" }
  | { status: "success"; data: T }
  | { status: "error"; error: string };
// Compare this with { loading: boolean; data?: T; error?: string },
// which allows loading=true AND error set at the same time.
```

- **Pitfall:** without narrowing, you can only use members that **every** type in the union has. For example, `s.radius` is an error before the `kind` check.
- **Follow-up:** this is also how Redux actions and NestJS/CQRS events are usually typed.

</details>

**68. What is an intersection type (`&`)? Write an example combining two interfaces.**

<details>
<summary>Answer</summary>

An intersection `A & B` is a type that has **all the members of A and all the members of B**: the value must satisfy both types. It's the type-level version of combining or mixing objects.

```ts
interface Person { name: string }
interface Employee { employeeId: number; department: string }

type Staff = Person & Employee;

const s: Staff = { name: "Ritesh", employeeId: 101, department: "Engineering" };
// Leaving out any property of either interface is a compile error.

// Common pattern: generic helpers that add fields
function withTimestamps<T extends object>(obj: T): T & { createdAt: Date } {
  return { ...obj, createdAt: new Date() };
}
const saved = withTimestamps(s); // has name, employeeId, department, createdAt
```

| | Union `A \| B` | Intersection `A & B` |
|---|---|---|
| Value must be | Either A or B | Both A and B |
| Members you can use | Only the shared ones | All of them |

- **Pitfall:** if both sides have a property with incompatible types, that property becomes `never`. For example, `{ id: string } & { id: number }` gives `id: never`, so `{ id: "a" }` fails with "Type 'string' is not assignable to type 'never'". With `interface B extends A`, the same conflict is reported right away as "Interface 'B' incorrectly extends interface 'A'".

</details>

**69. What is `keyof`? Write a function using `keyof` to safely access object properties.**

<details>
<summary>Answer</summary>

`keyof T` produces a **union of T's property names as literal types**. For `{ id: number; name: string }` that's `"id" | "name"`. Combined with generics and indexed access `T[K]`, it lets you write functions that only accept valid keys and return the correct type for each key.

```ts
function getProp<T, K extends keyof T>(obj: T, key: K): T[K] {
  return obj[key];
}

const user = { id: 1, name: "Ritesh", active: true };

const n = getProp(user, "name");   // type: string
const a = getProp(user, "active"); // type: boolean
console.log(n); // Ritesh
// getProp(user, "email");
// ❌ Error: Argument of type '"email"' is not assignable to parameter of type '"active" | "id" | "name"'.

function setProp<T, K extends keyof T>(obj: T, key: K, value: T[K]): void {
  obj[key] = value;
}
setProp(user, "id", 2);      // ✅
// setProp(user, "id", "2"); // ❌ Error: Argument of type 'string' is not assignable to parameter of type 'number'.

function pluck<T, K extends keyof T>(items: T[], key: K): T[K][] {
  return items.map((i) => i[key]);
}
console.log(pluck([user, { id: 3, name: "Amit", active: false }], "name")); // [ 'Ritesh', 'Amit' ]
```

**Walkthrough:** `K extends keyof T` limits `key` to real keys. `T[K]` looks up that key's type, so the return type follows the key you pass.

- **Pitfall:** `keyof` of a type with a string index signature is `string | number`, because numeric keys are converted to strings in JS.
- **Follow-up:** `Object.keys(obj)` returns `string[]`, not `(keyof T)[]`, because at runtime an object can have extra keys. You need an explicit cast if you want the narrower type.

</details>

**70. What is `typeof` in TypeScript type position? How is it different from JS `typeof`?**

<details>
<summary>Answer</summary>

In a **type position**, `typeof x` gets the **static TypeScript type of a variable or value** at compile time and gets erased from the output. In an **expression position**, it's the JS runtime operator that returns a string such as `"object"` or `"string"`.

| | TS `typeof` (type position) | JS `typeof` (runtime) |
|---|---|---|
| Where | `type X = typeof value` | `if (typeof v === "string")` |
| Result | A full TypeScript type | One of 8 strings |
| When | Compile time (erased) | Runtime |

```ts
const config = { apiUrl: "https://api.example.com", retries: 3 };

type Config = typeof config;     // { apiUrl: string; retries: number }
console.log(typeof config);      // object  (runtime operator)

// Get a union type from a constant array (single source of truth)
const ROLES = ["admin", "editor", "viewer"] as const;
type Role = (typeof ROLES)[number]; // "admin" | "editor" | "viewer"

// Use with utility types (they need a type, not a value)
function createUser(name: string) {
  return { id: crypto.randomUUID(), name, createdAt: new Date() };
}
type NewUser = ReturnType<typeof createUser>;
```

- **Pitfall:** type-level `typeof` only works on **identifiers and property accesses** (`typeof obj.a`), not on arbitrary expressions such as `typeof fn()`.
- **Follow-up:** the runtime `typeof` inside an `if` is also a **type guard**: TypeScript narrows the variable in that branch.

</details>

**71. What is type inference? When should you add explicit type annotations?**

<details>
<summary>Answer</summary>

Type inference is TypeScript **working out types from the values and code you write** without an annotation. It infers variable types from initializers, return types from `return` statements, and generic arguments from call arguments. A good rule is **let inference handle local code, and annotate at boundaries**.

```ts
let count = 0;            // number
const status = "active";  // "active" (literal type, because const)
const ids = [1, 2, 3];    // number[]
const doubled = ids.map((x) => x * 2); // x inferred as number (contextual typing)
```

**Add explicit annotations when:**
1. **Function parameters.** They are never inferred from how the function is called (you get implicit `any`, which is an error in strict mode).
2. **Exported/public function return types.** They lock the contract, catch accidental changes, and speed up type-checking in big projects.
3. **Empty or later-assigned values:** `const items: string[] = []`, `let user: User | null = null`.
4. **Object literals that must match a type.** Annotate the variable, or use `satisfies` to check it while keeping the narrow inferred type:

```ts
type Theme = { color: string; size: number };
const theme = { color: "red", size: 12 } satisfies Theme; // checked + keeps literal info
```

- **Pitfall:** don't annotate what's already obvious (`const x: number = 5`). It's just noise.
- **Pitfall:** `let status = "active"` widens to `string`, while `const` keeps `"active"`. This matters when passing the value to a union-typed parameter.

</details>

**72. What are generic constraints (`T extends SomeType`)? Write an example.**

<details>
<summary>Answer</summary>

A generic constraint **limits which types can be used for a type parameter**. `T extends X` means "T can be any type, as long as it's assignable to X". That lets you use X's members inside the function and still keep the caller's specific type.

```ts
// Anything with a length
function getLength<T extends { length: number }>(x: T): number {
  return x.length;
}
console.log(getLength("abc"), getLength([1, 2])); // 3 2
// getLength(10);
// ❌ Error: Argument of type 'number' is not assignable to parameter of type '{ length: number; }'.

// Practical: works on any entity with an id and keeps its full type
function indexById<T extends { id: number }>(items: T[]): Map<number, T> {
  return new Map(items.map((i) => [i.id, i]));
}
const byId = indexById([{ id: 1, name: "Ritesh" }, { id: 2, name: "Amit" }]);
console.log(byId.get(2)?.name); // Amit  (T is { id: number; name: string })

// Constraining one parameter by another
function getProp<T, K extends keyof T>(obj: T, key: K): T[K] {
  return obj[key];
}
```

**Why not just take `{ id: number }[]`?** You'd lose the specific type: `byId.get(2)?.name` would be an error. With a constraint you get both safety and the precise type.

- **Follow-up:** constraints can be combined with defaults: `<T extends object = {}>`.

</details>

**73. Write a generic `Stack<T>` class with `push`, `pop`, and `peek` methods.**

<details>
<summary>Answer</summary>

A stack is LIFO (last in, first out). Store the items in a private array and use the end of the array as the top, so every operation is O(1).

```ts
class Stack<T> {
  private items: T[] = [];

  push(item: T): void {
    this.items.push(item);
  }

  pop(): T | undefined {
    return this.items.pop();
  }

  peek(): T | undefined {
    return this.items[this.items.length - 1];
  }

  isEmpty(): boolean {
    return this.items.length === 0;
  }

  get size(): number {
    return this.items.length;
  }
}

const stack = new Stack<number>();
stack.push(10);
stack.push(20);
console.log(stack.peek());    // 20
console.log(stack.pop());     // 20
console.log(stack.size);      // 1
console.log(stack.pop());     // 10
console.log(stack.pop());     // undefined
console.log(stack.isEmpty()); // true
// stack.push("x"); // ❌ Error: Argument of type 'string' is not assignable to parameter of type 'number'.
```

**Walkthrough:**
- `T` is fixed when the stack is created (`new Stack<number>()`), so `push` only accepts `T` and `pop`/`peek` return `T`.
- `pop`/`peek` return `T | undefined` so callers have to handle the empty-stack case under strict mode. You could throw instead, but that changes the contract.
- `private` hides the array, so callers can't reach in and break the LIFO order. Use `#items` if you need true runtime privacy.

**Complexity:** `push`, `pop`, `peek`, `size` are all O(1) (amortized for `push`). Space is O(n).

</details>

**74. What is the difference between `Partial<T>`, `Required<T>`, `Readonly<T>`, and `Pick<T, K>`?**

<details>
<summary>Answer</summary>

They are built-in mapped types that produce a new type from `T`. The first three change **property modifiers**. `Pick` chooses a **subset of keys**.

| Utility | Effect | Typical use |
|---|---|---|
| `Partial<T>` | All properties optional (`?`) | PATCH/update payloads, form drafts |
| `Required<T>` | All properties required (removes `?`) | Config after defaults are applied |
| `Readonly<T>` | All properties `readonly` | Immutable state, frozen config |
| `Pick<T, K>` | Only keys `K` | Lightweight views, list-item DTOs |

```ts
interface User { id: number; name: string; email?: string }

type A = Partial<User>;          // { id?: number; name?: string; email?: string }
type B = Required<User>;         // { id: number; name: string; email: string }
type C = Readonly<User>;         // { readonly id: number; readonly name: string; readonly email?: string }
type D = Pick<User, "id" | "name">; // { id: number; name: string }

function updateUser(id: number, patch: Partial<User>) {
  return { id, ...patch };
}
updateUser(1, { name: "New" }); // ✅ only send what changed
```

How they're defined (useful for the follow-up "implement Partial"):

```ts
type MyPartial<T> = { [K in keyof T]?: T[K] };
type MyRequired<T> = { [K in keyof T]-?: T[K] };
type MyReadonly<T> = { readonly [K in keyof T]: T[K] };
type MyPick<T, K extends keyof T> = { [P in K]: T[P] };
```

- **Pitfall:** all of them are **shallow**. `Partial<User>` doesn't make nested objects' fields optional. You need a recursive `DeepPartial` for that.

</details>

**75. What does `Omit<T, K>` do? When would you use it? Give a practical example.**

<details>
<summary>Answer</summary>

`Omit<T, K>` creates a type with **every property of T except the keys in K**. It's the opposite of `Pick`. Use it when you want "the same shape minus a few fields", typically server-generated fields or sensitive ones.

```ts
interface UserEntity {
  id: number;
  name: string;
  email: string;
  password: string;
  createdAt: Date;
}

// Client doesn't send server-generated fields
type CreateUserDto = Omit<UserEntity, "id" | "createdAt">;
// { name: string; email: string; password: string }

// Never expose the password in API responses
type PublicUser = Omit<UserEntity, "password">;

function toPublic({ password, ...rest }: UserEntity): PublicUser {
  return rest;
}
```

In NestJS you'd often use `OmitType(CreateUserDto, [...])` from `@nestjs/mapped-types`. It does the same thing and also keeps the validation decorators.

- **Pitfall:** `Omit` doesn't check that the keys exist. `Omit<UserEntity, "pasword">` (typo) compiles and removes nothing. For a strict version: `type StrictOmit<T, K extends keyof T> = Omit<T, K>`.
- **Pitfall:** `Omit` on a union **doesn't distribute**. It flattens the union to the keys the members share and loses the discriminated shape. Use a distributive version:

```ts
type DistributiveOmit<T, K extends PropertyKey> = T extends unknown ? Omit<T, K> : never;
```

</details>

**76. What is `ReturnType<T>` and how would you use it?**

<details>
<summary>Answer</summary>

`ReturnType<T>` takes a **function type** and gives you its return type. Use it so the type **comes from the implementation** and you don't have to declare it twice. It's typical for factory functions, hooks, store/selectors, and third-party functions whose return types aren't exported.

```ts
function createStore() {
  let count = 0;
  return { get: () => count, inc: () => ++count };
}
type Store = ReturnType<typeof createStore>;
// { get: () => number; inc: () => number }

async function fetchUser() {
  return { id: 1, name: "Ritesh" };
}
type R1 = ReturnType<typeof fetchUser>;          // Promise<{ id: number; name: string }>
type R2 = Awaited<ReturnType<typeof fetchUser>>; // { id: number; name: string }
```

How it works under the hood (a conditional type with `infer`):

```ts
type MyReturnType<T extends (...args: any) => any> =
  T extends (...args: any) => infer R ? R : any;
```

Related utilities: `Parameters<typeof fn>` (a tuple of the argument types), `InstanceType<typeof SomeClass>`, `Awaited<T>`.

- **Pitfall:** you have to pass a **type**, not a value. `ReturnType<fetchUser>` gives "❌ Error: 'fetchUser' refers to a value, but is being used as a type here. Did you mean 'typeof fetchUser'?"
- **Pitfall:** for async functions, remember to wrap with `Awaited` to get the resolved value's type.
- **Follow-up:** Redux Toolkit's `type RootState = ReturnType<typeof store.getState>` is the classic real-world example.

</details>

**77. What is `NonNullable<T>`? How is it useful with API responses?**

<details>
<summary>Answer</summary>

`NonNullable<T>` **removes `null` and `undefined` from a type**. So `NonNullable<string | null | undefined>` is `string`. Today it's defined as `T & {}`. It's useful because API types usually mark fields as nullable, but after you've validated or filtered the data you want the non-null type.

```ts
interface ApiUser {
  id: number;
  email: string | null;
  manager?: { name: string } | null;
}

type Email = NonNullable<ApiUser["email"]>;     // string
type Manager = NonNullable<ApiUser["manager"]>; // { name: string }

// Generic type guard: filter out nulls and narrow the array type
function isDefined<T>(v: T): v is NonNullable<T> {
  return v !== null && v !== undefined;
}

const users: ApiUser[] = [
  { id: 1, email: "a@x.com" },
  { id: 2, email: null },
];
const emails = users.map((u) => u.email).filter(isDefined); // string[]
console.log(emails); // [ 'a@x.com' ]
```

**Common uses:** typing a component prop that is only rendered after a null check (`user: NonNullable<Data["user"]>`), typing helper functions that run after validation, and GraphQL codegen types where almost everything is nullable.

- **Pitfall:** `NonNullable` only changes the **type**. It doesn't check anything at runtime. Always pair it with a real check (a guard, `??`, or schema validation).
- **Follow-up:** since TS 5.5, `.filter((e) => e !== null)` infers the type predicate by itself and gives `string[]`. On older versions it stays `(string | null)[]`, which is why the `isDefined` helper is common.

</details>

**78. What are conditional types in TypeScript? Write a type that unwraps a Promise.**

<details>
<summary>Answer</summary>

A conditional type is a **type-level ternary**: `T extends U ? X : Y`. If `T` is assignable to `U`, the result is `X`, otherwise `Y`. With `infer` you can **capture part of the matched type** into a new type variable. That's how `ReturnType`, `Awaited` and `Parameters` are built.

```ts
type UnwrapPromise<T> = T extends Promise<infer U> ? U : T;

type A = UnwrapPromise<Promise<string>>;          // string
type B = UnwrapPromise<number>;                   // number (not a Promise, returned as-is)
type C = UnwrapPromise<Promise<Promise<number>>>; // Promise<number> (only one level)

// Recursive version: unwraps nested promises
type DeepUnwrap<T> = T extends Promise<infer U> ? DeepUnwrap<U> : T;
type D = DeepUnwrap<Promise<Promise<number>>>;    // number
```

In real code, use the built-in **`Awaited<T>`**. It unwraps recursively and also handles non-Promise "thenables".

**Distributive behaviour:** when `T` is a bare type parameter and you pass a union, the condition is applied to each member separately:

```ts
type ToArray<T> = T extends unknown ? T[] : never;
type E = ToArray<string | number>;   // string[] | number[]

type ToArrayND<T> = [T] extends [unknown] ? T[] : never; // wrapping in [] turns distribution off
type F = ToArrayND<string | number>; // (string | number)[]
```

- **Pitfall:** distribution is why `Exclude<T, U> = T extends U ? never : T` works. It's also why `never` passed to a distributive conditional type gives `never` (an empty union).

</details>

**79. What is a mapped type? Write a `Nullable<T>` mapped type.**

<details>
<summary>Answer</summary>

A mapped type **builds a new object type by looping over keys** with `[K in Keys]`, usually `keyof T`, and transforming each property's type or modifiers. `Partial`, `Readonly`, `Pick` and `Record` are all mapped types.

```ts
type Nullable<T> = { [K in keyof T]: T[K] | null };

interface Profile { name: string; age: number }

type NullableProfile = Nullable<Profile>;
// { name: string | null; age: number | null }

const draft: Nullable<Profile> = { name: "Ritesh", age: null }; // ✅ e.g. form state before input
```

**Modifiers and key remapping:**

```ts
type Mutable<T> = { -readonly [K in keyof T]: T[K] }; // remove readonly
type Concrete<T> = { [K in keyof T]-?: T[K] };        // remove ?  (like Required)
type Getters<T> = {                                     // rename keys with `as`
  [K in keyof T as `get${Capitalize<string & K>}`]: () => T[K];
};
```

**Walkthrough:** `keyof T` gives the union of keys. `K in ...` loops over them. `T[K]` is the original property type, which we widen with `| null`. Mapped types over `keyof T` keep the original `?`/`readonly` modifiers (they are "homomorphic").

- **Pitfall:** `Nullable<T>` is shallow, so nested objects aren't made nullable. A deep version recurses with a conditional: `T[K] extends object ? DeepNullable<T[K]> | null : T[K] | null`.

</details>

**80. What is a template literal type? Write a type that creates getter names from property names.**

<details>
<summary>Answer</summary>

Template literal types use JS template-string syntax **at the type level** to build string literal types, e.g. `` `on${Capitalize<T>}` ``. When given a union, they produce every combination. Together with the built-in helpers `Uppercase`, `Lowercase`, `Capitalize` and `Uncapitalize`, and mapped-type key remapping (`as`), they can generate strongly typed APIs from property names.

```ts
type Getters<T> = {
  [K in keyof T as `get${Capitalize<string & K>}`]: () => T[K];
};

type UserGetters = Getters<{ name: string; age: number }>;
// { getName: () => string; getAge: () => number }

// Runtime implementation that matches the type
function createGetters<T extends object>(obj: T): Getters<T> {
  const result: Record<string, () => unknown> = {};
  for (const key of Object.keys(obj) as (keyof T & string)[]) {
    result[`get${key[0].toUpperCase()}${key.slice(1)}`] = () => obj[key];
  }
  return result as Getters<T>;
}

const g = createGetters({ name: "Ritesh", age: 25 });
console.log(g.getName(), g.getAge()); // Ritesh 25
```

**Walkthrough:** `string & K` removes `number`/`symbol` keys, because `Capitalize` only accepts strings. `as` renames each key, and the value type becomes a function that returns the original `T[K]`.

More examples:

```ts
type EventName<T extends string> = `on${Capitalize<T>}`;
type E = EventName<"click" | "hover">;   // "onClick" | "onHover"

type Method = "GET" | "POST";
type Route = `${Method} /users`;         // "GET /users" | "POST /users"
```

- **Pitfall:** unions multiply. Three unions of 10 members each give 1000 literal types, which can slow the compiler or hit its complexity limit.
- **Follow-up:** the runtime version still needs an `as` cast, because TypeScript can't prove that string concatenation produces the remapped keys.

</details>
