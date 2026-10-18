**81. What are TypeScript decorators? What are the four types of decorators?**

<details>
<summary>Answer</summary>

A decorator is a function, applied with `@expr`, that TypeScript calls **when the class is defined** (not when you create an instance). It can look at a class or one of its members and add to it or replace it. The four classic kinds are **class, method, property and parameter** decorators. Accessor (getter/setter) decorators work like method decorators.

This is how NestJS works: `@Controller()` and `@Injectable()` are class decorators, `@Get()` is a method decorator, and `@Body()` and `@Param()` are parameter decorators. TypeORM's `@Column()` is a property decorator.

| Kind | Legacy signature (`experimentalDecorators`) | Typical use |
|---|---|---|
| Class | `(constructor)` | Register metadata, wrap the constructor |
| Method / accessor | `(target, key, descriptor)` | Logging, caching, routing |
| Property | `(target, key)` | ORM columns, validation metadata |
| Parameter | `(target, key, index)` | DI tokens, `@Body()` |

```ts
// tsconfig: "experimentalDecorators": true
function Controller(prefix: string) {                  // 1. class decorator (factory)
  return (target: Function) => {
    (target as any).prefix = prefix;
  };
}
function Log(target: object, key: string, desc: PropertyDescriptor) { // 2. method
  const original = desc.value;
  desc.value = function (...args: unknown[]) {
    console.log(`calling ${key}(${args.join(', ')})`);
    return original.apply(this, args);
  };
}
function Column(target: object, key: string) {        // 3. property
  console.log(`property decorator: ${key}`);
}
function Param(target: object, key: string, index: number) { // 4. parameter
  console.log(`param decorator: ${key} arg #${index}`);
}

@Controller('/users')
class UserController {
  @Column name = 'users';

  @Log
  find(@Param id: number) {
    return `user ${id}`;
  }
}

console.log(new UserController().find(7));
console.log((UserController as any).prefix);
// property decorator: name       ← runs at class definition
// param decorator: find arg #0   ← parameter before its method
// calling find(7)
// user 7
// /users
```

- **Order:** member decorators run first, from top to bottom. Parameter decorators run before the method they belong to. The class decorator runs last.
- **Follow-up:** TypeScript 5.0 added **standard (TC39) decorators**, which work without any flag. Their signature is `(value, context)`. They add `accessor` auto-accessor decorators but have **no parameter decorators**. NestJS still relies on the legacy mode.

</details>

**82. What do `experimentalDecorators` and `emitDecoratorMetadata` do in `tsconfig`?**

<details>
<summary>Answer</summary>

`experimentalDecorators` switches TypeScript to the **legacy (stage-2) decorator** implementation, the one NestJS, TypeORM and class-validator use. `emitDecoratorMetadata` makes the compiler also emit **type information as runtime metadata** for every decorated declaration: `design:type`, `design:paramtypes` and `design:returntype`. This is written through `Reflect.metadata`, which you get by importing the `reflect-metadata` polyfill.

Type information normally disappears at compile time. This flag keeps a small part of it. NestJS dependency injection reads `design:paramtypes` to find out which classes to inject into a constructor.

```ts
import { UsersService } from './svc.js';
function Injectable(): ClassDecorator { return () => {}; }

@Injectable()
export class UsersController {
  constructor(private readonly usersService: UsersService) {}
}
```

The compiled JS contains:

```js
exports.UsersController = UsersController = __decorate([
    Injectable(),
    __metadata("design:paramtypes", [svc_js_1.UsersService])
], UsersController);
```

So Nest can read `Reflect.getMetadata('design:paramtypes', UsersController)`, which gives `[UsersService]`, and then resolve that class from its container.

- **Pitfall:** only **classes** survive as metadata. An interface or type alias becomes `Object`, because interfaces don't exist at runtime. That is why Nest needs `@Inject('TOKEN')` for interface-based providers.
- **Pitfall:** both flags only matter for legacy decorators. Tools like esbuild and Vite's default transform don't emit metadata, so Nest projects use `tsc` or SWC with metadata turned on.

</details>

**83. What is `strictNullChecks`? What changes in your code when you enable it?**

<details>
<summary>Answer</summary>

With `strictNullChecks` (part of `strict`), `null` and `undefined` are **separate types**. They are no longer silently allowed in every type. A `string` can then never be `null`. If a value may be missing, its type has to say so (`string | null`), and you must narrow it before you use it.

What changes in your code:
- Functions that may return nothing get honest types. For example, `Array.prototype.find` returns `T | undefined` and `Map.get` returns `V | undefined`.
- Optional params and props (`s?: string`) become `string | undefined`.
- You write narrowing code: `if (x)`, `?.`, `??`, early returns, or a type guard.
- Class fields must be initialized (with `strictPropertyInitialization`).

```ts
interface User { id: number; name: string }
const users: User[] = [{ id: 1, name: 'Asha' }];

const user = users.find(u => u.id === 2); // User | undefined
console.log(user.name);        // ❌ Error: 'user' is possibly 'undefined'.

if (user) console.log(user.name.toUpperCase()); // ✅ narrowed to User
console.log(user?.name ?? 'Guest');              // ✅

let token: string = null;      // ❌ Error: Type 'null' is not assignable to type 'string'.
function len(s?: string) { return s.length; } // ❌ Error: 's' is possibly 'undefined'.
```

- **Why it matters:** without the flag, this whole class of "Cannot read properties of undefined" crashes type-checks fine. Always turn it on for new code.
- **Follow-up:** `noUncheckedIndexedAccess` goes one step further and makes `arr[i]` and `record[key]` return `T | undefined`.

</details>

**84. What is the `!` non-null assertion operator? When should (and shouldn't) you use it?**

<details>
<summary>Answer</summary>

Writing `expr!` tells the compiler "this is not `null` or `undefined`, trust me". It removes `null | undefined` from the type. It is a **compile-time-only** assertion: it gets erased, and **no runtime check** happens. If you are wrong, the code crashes later with the usual `undefined` error.

**Reasonable uses** (you know something the compiler can't prove):
- A DOM element you are sure exists: `document.getElementById('app')!`.
- `Map.get` right after `has`, where TS doesn't connect the two calls.
- The definite-assignment form on class fields that a framework or `init()` sets: `private repo!: Repo`.

**Avoid it** when the value really can be missing: API data, `find` results, env vars, user input. Narrow with a real check instead (`if`, `??`, an assertion function).

```ts
const el = document.getElementById('app')!;   // HTMLElement
el.textContent = 'hi';

class Service {
  private repo!: Map<string, number>;   // definite assignment assertion
  init() { this.repo = new Map(); }
}

const cache = new Map<string, number>();
if (cache.has('a')) {
  const v = cache.get('a')!;   // OK: has() guarantees it
}

const users: { name: string }[] = [];
const first = users.find(u => u.name === 'x')!; // compiles...
console.log(first.name); // 💥 TypeError: Cannot read properties of undefined (reading 'name')
```

- **Pitfall:** every `!` is a bet you're making by hand. In code review, prefer `?.`/`??`, or a function that throws a helpful error (`assertIsDefined`). Many teams ban `!` with the ESLint rule `@typescript-eslint/no-non-null-assertion`.

</details>

**85. What is a type guard? Write a custom type guard function using `is`.**

<details>
<summary>Answer</summary>

A type guard is a runtime check that TypeScript understands, so it **narrows the type** inside the branch where the check passed. Built-in guards are `typeof`, `instanceof`, `in`, equality checks and discriminant checks. A **custom type guard** is a function that returns `boolean` and has the return type `param is SomeType`.

```ts
interface Cat { kind: 'cat'; meow(): string }
interface Dog { kind: 'dog'; bark(): string }
type Pet = Cat | Dog;

function isCat(pet: Pet): pet is Cat {
  return pet.kind === 'cat';
}

function speak(pet: Pet) {
  if (isCat(pet)) return pet.meow(); // pet: Cat
  return pet.bark();                 // pet: Dog (else branch narrows too)
}

const pets: Pet[] = [
  { kind: 'cat', meow: () => 'meow' },
  { kind: 'dog', bark: () => 'woof' },
];
console.log(pets.map(speak));           // [ 'meow', 'woof' ]
const cats: Cat[] = pets.filter(isCat);  // guard also narrows filter()
console.log(cats.length);               // 1

const ids = [1, undefined, 3].filter(x => x !== undefined); // number[] (TS 5.5+ infers the predicate)
console.log(ids);                       // [ 1, 3 ]
```

- **Pitfall:** the compiler **does not check** that the function body matches the predicate. If `isCat` returned `true` for dogs, TS would still believe it. A wrong guard is as unsafe as `as`, so keep guards small and test them.
- **Follow-up:** before TS 5.5, `filter(x => x !== undefined)` did not narrow, and you had to write `filter((x): x is number => x !== undefined)`.

</details>

**86. What is an assertion function (`asserts value is T`)? How is it different from a type guard?**

<details>
<summary>Answer</summary>

An assertion function **throws if the condition fails**. If it returns normally, TypeScript narrows the variable **for the rest of the scope**. A type guard **returns a boolean** that you use in an `if`, and the narrowing applies only inside that branch.

| | Type guard | Assertion function |
|---|---|---|
| Signature | `(v): v is T` | `(v): asserts v is T` or `asserts cond` |
| Returns | `boolean` | `void` (throws on failure) |
| Narrowing scope | Inside the `if` branch | Everything after the call |
| Use when | You want to branch | Invalid data is a bug or bad input: fail fast |

```ts
function assertIsDefined<T>(value: T, msg?: string): asserts value is NonNullable<T> {
  if (value === undefined || value === null) {
    throw new Error(msg ?? 'Expected value to be defined');
  }
}

function assert(condition: unknown, msg: string): asserts condition {
  if (!condition) throw new Error(msg);
}

function getPort(env: Record<string, string | undefined>) {
  const port = env.PORT;          // string | undefined
  assertIsDefined(port, 'PORT is required');
  return Number(port);            // port: string from here on, no if-block needed
}

console.log(getPort({ PORT: '3000' })); // 3000
try {
  getPort({});
} catch (e) {
  console.log((e as Error).message);    // PORT is required
}

const x: unknown = 5;
assert(typeof x === 'number', 'not a number');
console.log(x.toFixed(1));  // 5.0
```

- **Pitfall:** if you write the assertion as an arrow function without an explicit type annotation, calling it fails with: ❌ `Assertions require every name in the call target to be declared with an explicit type annotation.` Use a `function` declaration, or annotate the const: `const assertStr: (v: unknown) => asserts v is string = ...`.
- Node's `assert` module is typed as an assertion function too, so `assert(user)` narrows `user`.

</details>

**87. What is the difference between structural typing and nominal typing? Which does TypeScript use?**

<details>
<summary>Answer</summary>

**Nominal typing** (Java, C#) decides compatibility by the **declared name** or inheritance: a `Vector` is a `Point` only if it says `implements Point`. **Structural typing** decides by **shape**: anything with the required members is compatible. **TypeScript is structural** ("duck typing" checked at compile time), which fits how JavaScript objects actually behave.

```ts
interface Point { x: number; y: number }
class Vector { constructor(public x: number, public y: number) {} }

function describe(p: Point) { return `${p.x},${p.y}`; }
console.log(describe(new Vector(1, 2)));   // 1,2 — Vector never declares Point
console.log(describe({ x: 3, y: 4 }));     // 3,4
```

The downside is that two IDs that are both `number` can be mixed up. To get nominal-like safety, use **branded types**:

```ts
type UserId = number & { readonly __brand: 'UserId' };
type OrderId = number & { readonly __brand: 'OrderId' };
const toUserId = (n: number) => n as UserId;   // validate here in real code

function getUser(id: UserId) { return id; }
getUser(toUserId(42));  // ✅
getUser(42);            // ❌ Error: Argument of type 'number' is not assignable to parameter of type 'UserId'.
getUser(7 as OrderId);  // ❌ Error: Argument of type 'OrderId' is not assignable to parameter of type 'UserId'.
```

- **Follow-up:** classes with `private` or `#private` members behave nominally. Two classes with the same private field are **not** compatible with each other.
- **Follow-up:** excess property checks (an error on an extra key in an object literal) are a special case for fresh literals. They don't mean TypeScript is nominal.

</details>

**88. What is `infer` in TypeScript? Write a type that extracts the first argument type of a function.**

<details>
<summary>Answer</summary>

`infer X` can only be used inside the `extends` clause of a **conditional type**. It declares a type variable that TypeScript fills in by **pattern-matching** the checked type. You can then use `X` in the true branch. Built-ins like `ReturnType`, `Parameters` and `Awaited` are written with it.

```ts
type FirstArg<F> = F extends (first: infer A, ...rest: any[]) => any ? A : never;

function createUser(name: string, age: number) { return { name, age }; }

type A = FirstArg<typeof createUser>;   // string
type B = FirstArg<() => void>;          // unknown  (no first param to match)
type C = FirstArg<number>;              // never    (not a function)

// Same idea, other shapes:
type ElementType<T> = T extends readonly (infer U)[] ? U : T;
type D = ElementType<string[]>;          // string
type Unwrap<T> = T extends Promise<infer V> ? V : T;
type E = Unwrap<Promise<number>>;        // number

// Built-in equivalent:
type P = Parameters<typeof createUser>[0]; // string
```

How it works: TS tries to match `F` against the pattern `(first: ?, ...rest) => any`. If that succeeds, `A` is bound to whatever sits in the `?` position. If it fails, the result is the false branch (`never`).

- **Follow-up:** `infer` can have a constraint: `T extends [infer H extends string, ...unknown[]] ? H : never`.
- **Follow-up:** with overloaded functions, `infer` only sees the **last** overload signature.

</details>

**89. What are recursive types? Write a `DeepPartial<T>` type.**

<details>
<summary>Answer</summary>

A recursive type **refers to itself** in its own definition. You need one for tree-like data: JSON, nested configs, comment threads, file trees. TypeScript supports recursion in type aliases, interfaces, mapped types and conditional types.

```ts
type Json = string | number | boolean | null | Json[] | { [key: string]: Json };

type DeepPartial<T> =
  T extends (...args: any[]) => unknown ? T :           // leave functions alone
  T extends readonly (infer U)[] ? DeepPartial<U>[] :   // recurse into arrays
  T extends object ? { [K in keyof T]?: DeepPartial<T[K]> } :
  T;                                                    // primitives stop recursion

interface Config {
  db: { host: string; port: number; pool: { min: number; max: number } };
  features: { name: string; enabled: boolean }[];
  log: (msg: string) => void;
}

const override: DeepPartial<Config> = {
  db: { pool: { max: 20 } },          // ✅ nested keys optional
  features: [{ enabled: true }],       // ✅ array items partial too
};
const bad: DeepPartial<Config> = { db: { port: '5432' } };
// ❌ Error: Type 'string' is not assignable to type 'number'.
```

Walkthrough: a plain `Partial<T>` only makes the **top level** optional. `DeepPartial` maps over every key and calls itself on each value. The conditional branches stop the recursion at primitives, and they stop functions and arrays from being turned into odd mapped objects.

- **Use case:** a patch or override object for config merging, test fixtures, or `PATCH` DTOs.
- **Pitfall:** very deep or unbounded recursion can hit `Type instantiation is excessively deep and possibly infinite`. Keep recursive types simple, or cap the depth with a counter tuple.

</details>

**90. What is `as const`? How does it affect type inference?**

<details>
<summary>Answer</summary>

`as const` is a **const assertion**. It tells TypeScript to infer the **narrowest possible type**: literal types instead of widened `string` or `number`, `readonly` on every property, and arrays become `readonly` **tuples**. It is purely a type-level change, and nothing is frozen at runtime.

```ts
const a = { method: 'GET', retries: 3 };
// { method: string; retries: number }
const b = { method: 'GET', retries: 3 } as const;
// { readonly method: 'GET'; readonly retries: 3 }

function request(method: 'GET' | 'POST') { return method; }
request(a.method); // ❌ Error: Argument of type 'string' is not assignable to parameter of type '"GET" | "POST"'.
request(b.method); // ✅
b.retries = 4;     // ❌ Error: Cannot assign to 'retries' because it is a read-only property.

// Single source of truth: runtime array + derived union type
const ROLES = ['admin', 'editor', 'viewer'] as const;
type Role = (typeof ROLES)[number];              // 'admin' | 'editor' | 'viewer'
ROLES.push('owner'); // ❌ Error: Property 'push' does not exist on type 'readonly ["admin", "editor", "viewer"]'.

// Enum alternative
const STATUS = { ACTIVE: 'active', BANNED: 'banned' } as const;
type Status = (typeof STATUS)[keyof typeof STATUS]; // 'active' | 'banned'

const isRole = (x: string): x is Role => (ROLES as readonly string[]).includes(x);
console.log(isRole('admin'), isRole('owner'));   // true false
```

- **Why interviewers ask:** the "`as const` object + derived union" pattern is the modern replacement for `enum`. It is erasable syntax, tree-shakable, and needs no runtime enum object.
- **Pitfall:** `as const` does not call `Object.freeze`, so JS code can still mutate the object. Combine the two if you need runtime immutability.

</details>

**91. How do you type an object where you know the value type but not all keys (`Record<string, T>`)?**

<details>
<summary>Answer</summary>

Use `Record<string, T>` or the equivalent index signature `{ [key: string]: T }`. Both mean "any string key, and every value is `T`". If the keys come from a **known finite set**, use `Record<'a' | 'b', T>` instead, so that missing keys are caught.

```ts
const scores: Record<string, number> = { asha: 90, ravi: 75 };
const scores2: { [name: string]: number } = { asha: 90 };   // same thing

const s = scores['unknown'];   // type says number...
console.log(s);                // undefined  ← runtime disagrees!

type Env = 'dev' | 'prod';
const urls: Record<Env, string> = { dev: 'http://localhost', prod: 'https://api.x.com' };
const missing: Record<Env, string> = { dev: 'x' };
// ❌ Error: Property 'prod' is missing in type '{ dev: string; }' but required in type 'Record<Env, string>'.
const partial: Partial<Record<Env, string>> = { dev: 'x' };  // ✅ some keys

// Known keys + arbitrary extras
interface Headers { 'content-type': string; [key: string]: string }

// Frequently added/removed keys → Map
const counts = new Map<string, number>();
counts.set('a', (counts.get('a') ?? 0) + 1);
console.log(counts.get('a'));  // 1
```

| Need | Use |
|---|---|
| Arbitrary string keys, same value type | `Record<string, T>` |
| Fixed set of keys, all required | `Record<Union, T>` |
| Fixed set, some optional | `Partial<Record<Union, T>>` |
| Dynamic keys, frequent add/delete, non-string keys | `Map<K, V>` |

- **Pitfall:** by default `scores['x']` is typed `number` even when the key doesn't exist. Enable **`noUncheckedIndexedAccess`**, and the lookup becomes `number | undefined`, which forces a check.
- **Pitfall:** in an index signature with extra named properties, every named property must be assignable to the index value type.

</details>

**92. What is the `satisfies` operator in TypeScript? How is it different from type assertion (`as`)?**

<details>
<summary>Answer</summary>

`expr satisfies T` (TS 4.9+) **checks** that a value matches `T` but **keeps the value's own, narrower inferred type**. `as T` **overrides** the type without real checking. It only rejects conversions that are completely unrelated, so it can hide mistakes. Type annotations (`const x: T`) check the value but **widen** it to `T`.

| | `const x: T = v` | `v as T` | `v satisfies T` |
|---|---|---|---|
| Validates against `T` | ✅ | ❌ (mostly trusts you) | ✅ |
| Catches missing/extra keys | ✅ | ❌ | ✅ |
| Resulting type | `T` (widened) | `T` | inferred type of `v` (narrow) |

```ts
type Color = 'red' | 'green' | 'blue';
type RGB = [number, number, number];

const palette = {
  red: [255, 0, 0],
  green: '#00ff00',
  blue: [0, 0, 255],
} satisfies Record<Color, string | RGB>;

palette.green.toUpperCase();   // ✅ still known to be string
palette.red.map(n => n / 255); // ✅ still known to be RGB

const annotated: Record<Color, string | RGB> = { red: [255, 0, 0], green: '#0f0', blue: '#00f' };
annotated.green.toUpperCase();
// ❌ Error: Property 'toUpperCase' does not exist on type 'string | RGB'.

const bad = { red: [255, 0, 0], green: '#0f0' } satisfies Record<Color, string | RGB>;
// ❌ Error: Property 'blue' is missing ...
const typo = { red: '#f00', green: '#0f0', blue: '#00f', purple: '#f0f' } satisfies Record<Color, string>;
// ❌ Error: Object literal may only specify known properties, and 'purple' does not exist ...

const lie = { red: [255, 0, 0] } as Record<Color, string | RGB>; // compiles — `as` hides the missing keys
```

- **Rule of thumb:** use `satisfies` for config objects, route maps and lookup tables. Keep `as` for cases where you really do know more than the compiler (for example `as const`, or after runtime validation).

</details>

**93. How do you extend a third-party library's types using declaration merging?**

<details>
<summary>Answer</summary>

TypeScript **merges** declarations that share a name: interfaces, namespaces, and interfaces with classes. You add fields to a library's types by re-declaring its interface inside the **same scope**. For a module you use `declare module 'lib'` (module augmentation). For globals you use `declare global`. You can't add to a `type` alias, only to an `interface`.

The classic example: add `req.user` in Express or NestJS after an auth middleware.

```ts
// src/types/express.d.ts
import 'express';   // makes this file a module → declarations below AUGMENT, not replace

declare global {
  namespace Express {
    interface Request {
      user?: { id: number; role: 'admin' | 'user' };
    }
  }
}

// Module augmentation: add to an interface exported by a package
declare module 'express' {
  interface Router {
    health(): void;
  }
}
```

```ts
// src/types/global.d.ts — extend browser globals
export {};
declare global {
  interface Window { analytics: { track(event: string): void } }
}
```

```ts
import type { Request } from 'express';
function handler(req: Request) {
  return req.user?.role;          // ✅ typed, no `as any`
}
window.analytics.track('signup'); // ✅

interface Box { a: number }
interface Box { b: string }        // plain interface merging
const box: Box = { a: 1, b: 'x' }; // needs both
```

- **Pitfall:** without a top-level `import` or `export`, a `.d.ts` file is a *script*. Then `declare module 'express'` declares a **brand-new ambient module** that shadows the real types, instead of augmenting them.
- **Pitfall:** make sure the file is included by `tsconfig` (`include` or `typeRoots`). Otherwise the augmentation is silently ignored.

</details>

**94. What is a `.d.ts` file? When would you create one manually?**

<details>
<summary>Answer</summary>

A `.d.ts` file is a **declaration file**. It contains **only types** (signatures, interfaces, `declare` statements) and never emits JavaScript. It describes the shape of code that exists somewhere else at runtime. Libraries ship them (`"types"` in `package.json`) or get them from `@types/*`. `tsc --declaration` generates them from your own `.ts` files.

When to write one manually:
- A **JS library without types** (and no `@types` package).
- **Non-code imports** that your bundler handles: `.svg`, `.png`, `.css`, `.module.scss`.
- **Globals** injected by a script tag or the bundler (`__APP_VERSION__`, `window.analytics`).
- **Augmenting** existing types (Express `Request`, `ProcessEnv`). See Q93.
- Publishing a JS package with hand-written types.

```ts
// src/types/shims.d.ts   (no import/export → global script declarations)
declare module 'legacy-slugify' {
  export default function slugify(input: string, sep?: string): string;
}

declare module '*.svg' {
  const url: string;
  export default url;
}

declare const __APP_VERSION__: string;   // injected by Vite `define`

declare namespace NodeJS {
  interface ProcessEnv { DATABASE_URL: string }
}
```

```ts
import slugify from 'legacy-slugify';   // ✅ typed
import logo from './logo.svg';          // ✅ string
```

- **Quick escape hatch:** `declare module 'some-lib';` with no body types the whole module as `any`. It's fine to unblock yourself, but it removes all type safety.
- **Follow-up:** `skipLibCheck: true` skips type-checking every `.d.ts` file (your own included). That speeds up builds but can hide errors in declarations.

</details>

**95. What is the difference between `import type` and regular `import`?**

<details>
<summary>Answer</summary>

`import type { X }` imports **only the type**, and the whole statement is **always erased** from the JS output. A regular `import` may import values and types. Its type-only parts get elided, but the module can still be loaded at runtime (side effects, bundle size, circular imports).

```ts
// types.ts
export interface User { id: number }
export const fetchUser = (id: number): User => ({ id });
```

```ts
import type { User } from './types.js';               // erased completely
import { type User as U, fetchUser } from './types.js'; // inline: only fetchUser stays
```

Emitted JS for the second line: `import { fetchUser } from './types.js';`

Why it matters:
- **`verbatimModuleSyntax`** (recommended with ESM, and what tools like esbuild, SWC and Node type stripping assume) keeps every non-`type` import as written. Importing an interface without `type` then fails: ❌ `'User' is a type and must be imported using a type-only import when 'verbatimModuleSyntax' is enabled.`
- It helps break **circular dependencies** that only exist through types.
- It makes intent clear to readers and to single-file transpilers.

- **Pitfall (NestJS):** don't use `import type` for classes that are **injected**. With `emitDecoratorMetadata`, the compiler needs the runtime class. With `import type` it emits `__metadata("design:paramtypes", [Function])` instead of `[UsersService]`, and Nest fails to resolve the dependency.
- **Pitfall:** under `verbatimModuleSyntax`, `import { type A } from './x'` (all specifiers inline-typed) still emits `import {} from './x'`, so the module still loads. Use `import type` to drop it completely.

</details>

**96. What is `namespace` in TypeScript? Is it recommended in modern TypeScript? Why or why not?**

<details>
<summary>Answer</summary>

`namespace X { ... }` (formerly "internal modules") is TypeScript's pre-ES-modules way of grouping code under a named object. It **compiles to an IIFE** that builds an object. It is **not recommended** for application code today. **ES modules** (`import`/`export`) already give you file-level scoping, tree-shaking and standard tooling.

```ts
namespace Validation {
  export const isEmail = (s: string) => s.includes('@');
}
console.log(Validation.isEmail('a@b.com')); // true
```

Why to avoid it:
- It is **not standard JavaScript**: namespaces with runtime code need a real transform. Node's type stripping rejects them (`TypeScript namespace declaration is not supported in strip-only mode`). TS 5.8's `erasableSyntaxOnly` flag reports them as errors, together with `enum` and parameter properties.
- Bundlers can't tree-shake members inside the namespace object.
- Two layers of organization (files and namespaces) cause confusion.

Where namespaces are still fine or necessary (**type-only** usage):
- `.d.ts` files and global augmentation: `declare global { namespace Express { interface Request { ... } } }`.
- Describing legacy global libraries (`declare namespace NodeJS`).
- Merging types onto a function or class, like `function format` plus `namespace format` for static helpers (rare).

- **Follow-up:** `module Foo {}` is the old keyword for the same thing and is now deprecated in favour of `namespace`. `declare module 'x'` (with a string) is different: that is module augmentation or an ambient module declaration.

</details>

**97. How do you type `this` in a function in TypeScript?**

<details>
<summary>Answer</summary>

Declare a **fake first parameter named `this`**: `function f(this: User, ...)`. It is erased from the JS and doesn't count as a real argument. TypeScript then checks that every call site provides the right `this`. Turn on `noImplicitThis` (part of `strict`) so an untyped `this` becomes an error instead of `any`.

```ts
interface User { name: string }

function greet(this: User, greeting: string) {
  return `${greeting}, ${this.name}`;
}

const user = { name: 'Asha', greet };
console.log(user.greet('Hi'));                        // Hi, Asha
console.log(greet.call({ name: 'Ravi' }, 'Hello'));   // Hello, Ravi

greet('Hey');                 // ❌ Error: The 'this' context of type 'void' is not assignable to method's 'this' of type 'User'.
const detached = user.greet;
detached('Yo');               // ❌ same error: the classic "lost this" bug, caught at compile time

type T = ThisParameterType<typeof greet>;                      // User
const bound: OmitThisParameter<typeof greet> = greet.bind({ name: 'Kiran' });
console.log(bound('Namaste'));                                 // Namaste, Kiran
```

**The polymorphic `this` type** is used for fluent or builder APIs, so that subclasses keep their own type through the chain:

```ts
class QueryBuilder {
  private parts: string[] = [];
  where(c: string): this { this.parts.push(c); return this; }
  build() { return this.parts.join(' AND '); }
}
class UserQuery extends QueryBuilder {
  active(): this { return this.where('active = true'); }
}
console.log(new UserQuery().where('age > 18').active().build()); // age > 18 AND active = true
```

- **Follow-up:** in classes, arrow-function fields (`inc = () => { this.count++ }`) bind `this` lexically, so they are safe to pass as React or event callbacks.
- **Follow-up:** callbacks can require a `this` type too, for example `addEventListener`'s `this: HTMLElement`.

</details>

**98. How do you make a class property truly private in TypeScript vs using `private` keyword?**

<details>
<summary>Answer</summary>

Use the **JavaScript private field syntax `#field`**. The `private` keyword is **compile-time only**: it is erased, the property exists as a normal public property at runtime, and it can be reached through `as any`, bracket access, `JSON.stringify` or `Object.keys`. A `#field` is enforced by the **JS engine itself** (hard privacy). It can't be seen or accessed outside the class body at all.

```ts
class Account {
  private pin = 1234;       // TS-only privacy
  #balance = 500;           // real runtime privacy

  get balance() { return this.#balance; }
  static hasBalance(obj: object) { return #balance in obj; } // brand check
}

const acc = new Account();
acc.pin;       // ❌ Error: Property 'pin' is private and only accessible within class 'Account'.
acc.#balance;  // ❌ Error: Property '#balance' is not accessible outside class 'Account' because it has a private identifier.

console.log((acc as any).pin);          // 1234  — escape hatch works
console.log(acc['pin']);                // 1234  — bracket access is allowed by TS!
console.log((acc as any)['#balance']);  // undefined
console.log(JSON.stringify(acc));       // {"pin":1234}  ← leaked
console.log(Object.keys(acc));          // [ 'pin' ]
console.log(acc.balance);               // 500
console.log(Account.hasBalance(acc), Account.hasBalance({})); // true false
```

| | `private x` | `#x` |
|---|---|---|
| Enforced by | TS compiler only | JS runtime |
| Bypass | `as any`, `obj['x']` | Impossible |
| Shows in `JSON.stringify` / `Object.keys` | Yes | No |
| Subclass can redeclare same name | No (conflict) | Yes (separate slots) |
| Usable as constructor parameter property | Yes (`private readonly repo`) | No |

- **Guideline:** use `#` for real encapsulation (secrets, library internals). `private` is fine for everyday app code and is what NestJS constructor injection uses (`constructor(private readonly repo: Repo)`).
- **Pitfall:** `#` fields don't work through `Proxy` objects, because the brand check fails on the proxy.

</details>

**99. What is the `Awaited<T>` utility type and when do you need it?**

<details>
<summary>Answer</summary>

`Awaited<T>` computes the type you get from **`await`-ing a `T`**. It unwraps promises (and thenables) **recursively**, leaves non-promise types unchanged, and distributes over unions. You mostly need it to get the **resolved value type of an async function**, and when writing generic helpers around promises.

```ts
async function fetchUser(id: number) {
  return { id, name: 'Asha' };
}

type R1 = ReturnType<typeof fetchUser>;            // Promise<{ id: number; name: string }>
type User = Awaited<ReturnType<typeof fetchUser>>;  // { id: number; name: string }

type A = Awaited<Promise<Promise<number>>>;         // number (recursive)
type B = Awaited<string>;                           // string (non-promise passes through)
type C = Awaited<Promise<string> | number>;         // string | number (distributes)

async function main() {
  const [u, n] = await Promise.all([fetchUser(1), Promise.resolve(42)]);
  // Promise.all is typed with Awaited<T[P]> → u: User, n: number
  console.log(u.name, n.toFixed(1)); // Asha 42.0
}
main();

// Generic wrapper: T might itself be a Promise type
async function withRetry<T>(fn: () => Promise<T>): Promise<Awaited<T>> {
  return await fn();
}
```

Typical real uses:
- Deriving DTO or response types from service methods without duplicating them: `Awaited<ReturnType<UsersService['findOne']>>`.
- Typing the results of `Promise.all`, `Promise.race` and `Promise.allSettled` (the built-in lib uses it).
- React Server Components / Next.js: the type of data returned by an async loader.

- **Follow-up:** before TS 4.5 people wrote their own `T extends Promise<infer U> ? U : T`. That only unwraps one level and doesn't handle thenables. `Awaited` fixes both.

</details>

**100. You have a function that accepts `unknown`. Write the full chain of type narrowing to safely extract a `User` object with `id: number` and `name: string`, including a custom type guard and error handling.**

<details>
<summary>Answer</summary>

Narrow step by step, `unknown` → object → record with the right fields → `User`, using runtime checks the compiler understands. Wrap this in a reusable **type guard** (for branching or `filter`) and an **assertion function** (for fail-fast with precise messages). Return a typed `Result` so callers must handle failure.

```ts
interface User {
  id: number;
  name: string;
}

class ValidationError extends Error {
  constructor(message: string, public readonly field?: string) {
    super(message);
    this.name = 'ValidationError';
  }
}

// 1. unknown → indexable object (rules out null, primitives, arrays)
function isRecord(value: unknown): value is Record<string, unknown> {
  return typeof value === 'object' && value !== null && !Array.isArray(value);
}

// 2. Custom type guard
function isUser(value: unknown): value is User {
  return (
    isRecord(value) &&
    typeof value.id === 'number' &&
    Number.isInteger(value.id) &&
    typeof value.name === 'string' &&
    value.name.trim().length > 0
  );
}

// 3. Assertion function: same checks, but says WHAT is wrong
function assertUser(value: unknown): asserts value is User {
  if (!isRecord(value)) throw new ValidationError('Expected an object');
  if (typeof value.id !== 'number' || !Number.isInteger(value.id))
    throw new ValidationError('id must be an integer', 'id');
  if (typeof value.name !== 'string' || value.name.trim() === '')
    throw new ValidationError('name must be a non-empty string', 'name');
}

// 4. Full chain: raw string/object → unknown → User, errors as a Result
type Result<T> = { ok: true; value: T } | { ok: false; error: string };

function parseUser(input: unknown): Result<User> {
  try {
    const data: unknown = typeof input === 'string' ? JSON.parse(input) : input;
    assertUser(data);
    // data: User here — copy only known fields (drops extra props like `role`)
    return { ok: true, value: { id: data.id, name: data.name } };
  } catch (err) {
    if (err instanceof SyntaxError) return { ok: false, error: `Invalid JSON: ${err.message}` };
    if (err instanceof ValidationError) return { ok: false, error: err.message };
    throw err; // unexpected failure: don't swallow it
  }
}

const inputs: unknown[] = [
  '{"id": 1, "name": "Asha", "role": "admin"}',
  { id: '1', name: 'Ravi' },
  { id: 2 },
  '{bad json',
  null,
];
for (const i of inputs) console.log(parseUser(i));
// { ok: true, value: { id: 1, name: 'Asha' } }
// { ok: false, error: 'id must be an integer' }
// { ok: false, error: 'name must be a non-empty string' }
// { ok: false, error: "Invalid JSON: Expected property name or '}' in JSON at position 1 (line 1 column 2)" }
// { ok: false, error: 'Expected an object' }

const users = [{ id: 3, name: 'Kiran' }, 'junk', { id: 4 }].filter(isUser);
console.log(users); // [ { id: 3, name: 'Kiran' } ]
```

Walkthrough:
- `typeof value === 'object'` alone is not enough, because `typeof null === 'object'` and arrays are objects too. That is why `isRecord` exists.
- After `isRecord`, `value.id` is `unknown`, so each field needs its own `typeof` check. No `as` is used anywhere.
- `catch (err)` gives `err: unknown` (under `useUnknownInCatchVariables`, part of `strict`), so it is narrowed with `instanceof` before `.message` is read. Unknown errors are re-thrown.
- The `Result` union forces the caller to check `ok` before touching `value`.

- **Follow-up:** in production (NestJS DTOs, API responses) you would usually use a schema library such as **Zod** (`UserSchema.safeParse(data)`), or class-validator with `ValidationPipe`. These give you the same guard plus an inferred type from one definition. Hand-written guards are fine for small shapes and are what interviewers want to see you reason through.
- **Pitfall:** the JSON error message text depends on the JS engine, so don't assert on it in tests.

</details>
