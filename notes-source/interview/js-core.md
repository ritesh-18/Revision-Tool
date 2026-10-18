**21. Explain the scope chain with a nested function example.**

<details>
<summary>Answer</summary>

The scope chain is the ordered list of lexical environments JavaScript walks to resolve a variable: first the current function's scope, then the scope of the function it was *written* inside, and so on up to the global scope. If the name isn't found anywhere, you get a `ReferenceError`.

It is **lexical** (static): the chain is fixed by where the code is written, not by where the function is called from. Each function object keeps a hidden reference (`[[Environment]]`) to the scope it was created in, and that link is what forms the chain.

```js
const app = "global";
function outer() {
  const role = "outer";
  function inner() {
    const id = 42;
    console.log(id, role, app); // 42 outer global
  }
  inner();
}
outer();
```

Lookup for `app` inside `inner`: `inner` scope → `outer` scope → global scope → found.

- Inner scopes can read outer variables; outer scopes can't see inner ones.
- A variable declared in an inner scope with the same name **shadows** the outer one.
- `let`/`const` also create block scopes (`if`, `for`, a bare block), which are links in the chain too. `var` is only function-scoped.
- **Follow-up:** "Dynamic vs lexical scope?" JS scope is lexical. Only `this` is decided at call time, and it is not part of the scope chain.

</details>

**22. What is a closure? Write a function that uses closure to create a counter.**

<details>
<summary>Answer</summary>

A closure is a function bundled with a reference to the lexical scope it was created in, so it can keep reading and updating those variables after the outer function has returned. Every function in JS is a closure. It matters in practice when an inner function outlives its parent.

```js
function createCounter(start = 0) {
  let count = start; // private: only reachable via the closure
  return {
    increment: () => ++count,
    decrement: () => --count,
    value: () => count,
  };
}
const c1 = createCounter();
const c2 = createCounter(10);
c1.increment();
c1.increment();
console.log(c1.value()); // 2
console.log(c2.increment()); // 11  (each call gets its own `count`)
console.log(c1.count); // undefined  (truly private)
```

Walkthrough: every `createCounter()` call creates a new scope holding `count`. The returned functions keep a reference to that scope, so it isn't garbage-collected and stays private to them.

Real uses: data privacy / module pattern, memoization caches, `debounce`/`throttle`, function factories, and React hooks (a `useState` setter or an effect callback closes over that render's values).

- **Pitfall (classic loop question):**

```js
for (var i = 0; i < 3; i++) setTimeout(() => console.log(i)); // 3 3 3
for (let j = 0; j < 3; j++) setTimeout(() => console.log(j)); // 0 1 2
```

`var` gives one shared binding. `let` creates a fresh binding per iteration.
- **Pitfall:** Stale closures in React. A `setInterval` inside `useEffect(..., [])` sees the first render's state forever. Fix it with the functional updater `setX(x => x + 1)` or a ref.
- **Pitfall:** Closures keep their whole captured scope alive, which can leak memory (e.g. a big array captured by a long-lived listener).

</details>

**23. What is the difference between `.call()`, `.apply()`, and `.bind()`?**

<details>
<summary>Answer</summary>

All three set `this` explicitly. `call` and `apply` **invoke the function immediately**: `call` takes arguments one by one and `apply` takes them as an array. `bind` **does not invoke**. It returns a new function with `this` (and optionally some leading arguments) permanently fixed.

| | Invokes now? | Args | Returns |
|---|---|---|---|
| `fn.call(ctx, a, b)` | Yes | comma-separated | fn's result |
| `fn.apply(ctx, [a, b])` | Yes | array (or array-like) | fn's result |
| `fn.bind(ctx, a)` | No | partial args, rest later | new bound function |

```js
function greet(greeting, punct) {
  return `${greeting}, ${this.name}${punct}`;
}
const user = { name: "Asha" };
console.log(greet.call(user, "Hi", "!"));      // Hi, Asha!
console.log(greet.apply(user, ["Hello", "?"])); // Hello, Asha?
const bound = greet.bind(user, "Hey");          // partial application
console.log(bound("."));                        // Hey, Asha.
console.log(bound.call({ name: "X" }, "!"));    // Hey, Asha!  (bind wins; can't re-bind)
console.log(Math.max.apply(null, [3, 9, 1]));   // 9
```

- Mnemonic: **A**pply = **A**rray, **C**all = **C**ommas.
- These days `fn(...args)` / `fn.call(ctx, ...args)` covers most `apply` use cases.
- **Pitfall:** `call`/`apply`/`bind` have no effect on `this` in arrow functions, because arrows don't have their own `this`.
- **Pitfall:** A bound function's `this` can't be changed again, except by `new`, which ignores the bound `this`.
- **Follow-up:** You may be asked to write a `bind` polyfill: return `(...later) => fn.apply(ctx, [...early, ...later])`.

</details>

**24. How does `this` behave in regular functions vs arrow functions?**

<details>
<summary>Answer</summary>

In a **regular function**, `this` is decided at **call time** by how the function is called. **Arrow functions have no own `this`**. They capture it lexically from the surrounding scope when they're defined, and nothing (`call`, `bind`, `new`) can change it.

Regular function rules, from highest priority to lowest:

| Call style | `this` |
|---|---|
| `new Fn()` | the newly created object |
| `fn.call/apply/bind(obj)` | `obj` |
| `obj.fn()` | `obj` (whatever is left of the dot) |
| plain `fn()` | `undefined` in strict mode / modules / classes, `globalThis` in sloppy mode |

```js
"use strict";
const obj = {
  name: "obj",
  regular() { return this?.name; },
  arrow: () => this?.name,           // `this` of the enclosing module scope, not obj
  delayed() {
    setTimeout(function () { console.log("fn:", this === obj); }, 0); // fn: false
    setTimeout(() => console.log("arrow:", this === obj), 0);         // arrow: true
  },
};
console.log(obj.regular()); // obj
const r = obj.regular;
console.log(r());           // undefined  (method detached → lost `this`)
console.log(obj.arrow());   // undefined
obj.delayed();
```

- Use arrows for callbacks inside methods (the `delayed` case). Don't use them as object methods or prototype methods.
- Arrows also have no `arguments` and no `prototype`, and can't be used with `new`.
- **Pitfall:** Object literal braces do **not** create a scope, so `arrow` above does not see `obj` as `this`.

</details>

**25. How do you fix the "lost `this`" problem in callbacks?**

<details>
<summary>Answer</summary>

`this` gets lost when a method is passed as a bare function reference (`setTimeout(this.tick)`, `onClick={this.handle}`, `arr.map(obj.fn)`). The caller then invokes it as a plain function, so `this` becomes `undefined`. There are four fixes: `bind` it, wrap it in an arrow, define the method as an arrow class field, or pass `thisArg` where the API supports it.

```js
"use strict";
class Timer {
  seconds = 0;
  tickArrow = () => { this.seconds++; };            // 1. arrow class field
  tick() { this.seconds++; }
  start() {
    setTimeout(this.tick.bind(this), 0);            // 2. bind
    setTimeout(() => this.tick(), 0);               // 3. inline arrow wrapper
    setTimeout(this.tickArrow, 0);                  // works because of fix 1
    setTimeout(() => console.log(this.seconds), 5); // 3
  }
}
new Timer().start();

const t = new Timer();
try {
  const f = t.tick;
  f(); // ❌ TypeError: Cannot read properties of undefined (reading 'seconds')
} catch (e) {
  console.log(e.message);
}
```

| Fix | Notes |
|---|---|
| `this.fn.bind(this)` in the constructor | Classic React class-component pattern. Shared prototype method plus one bound copy. |
| Arrow class field | Cleanest to write. One function **per instance** (more memory) and not on the prototype, so it's harder to mock or override in tests. |
| Inline arrow `() => this.fn()` | Creates a new function each render/call, which can break memoization (`React.memo`, `useEffect` deps). |
| `thisArg` | `arr.forEach(fn, ctx)`, `arr.map(fn, ctx)` |

- **Follow-up:** In function components and NestJS services this rarely comes up. It does come up when you pass `this.service.method` as a callback (e.g. `.then(this.repo.save)`). Use `.then((x) => this.repo.save(x))` instead.

</details>

**26. What is the prototype chain? How does property lookup work?**

<details>
<summary>Answer</summary>

Every object has a hidden `[[Prototype]]` link to another object (or `null`). When you read `obj.prop`, JS checks `obj`'s **own** properties first. If `prop` isn't there, it follows `[[Prototype]]` and checks that object, and keeps going until it finds the property or reaches `null`, in which case the result is `undefined`. This linked list of objects is the prototype chain.

```js
const animal = { eats: true, describe() { return `eats=${this.eats}`; } };
const dog = Object.create(animal);
dog.barks = true;

console.log(dog.barks);                                  // true  (own)
console.log(dog.eats);                                   // true  (from animal)
console.log(dog.describe());                             // eats=true  (this = dog)
console.log(dog.fly);                                    // undefined (end of chain)
console.log(Object.getPrototypeOf(dog) === animal);      // true
console.log(Object.getPrototypeOf(animal) === Object.prototype); // true
console.log(Object.getPrototypeOf(Object.prototype));    // null
dog.eats = false;           // creates an own prop that shadows; animal is untouched
console.log(animal.eats);   // true
```

Key points:
- **Reads** walk the chain. **Writes** create or update an own property on the object (unless the chain has a setter or a non-writable property).
- `Fn.prototype` is the object that becomes `[[Prototype]]` of instances created with `new Fn()`. `__proto__` / `Object.getPrototypeOf` is an object's actual link. Interviewers like to ask about this difference.
- `[].map` works because `arr → Array.prototype → Object.prototype → null`.
- `hasOwnProperty` / `Object.hasOwn` check only own properties. `in` checks the whole chain.
- **Pitfall:** Long chains and changing prototypes at runtime (`Object.setPrototypeOf`) slow down engine optimizations.

</details>

**27. How does prototypal inheritance differ from classical inheritance?**

<details>
<summary>Answer</summary>

In classical inheritance (Java, C#), a class is a blueprint and instances are **copies** of its structure. The hierarchy is fixed at compile time. In prototypal inheritance, objects inherit **directly from other objects** through a live `[[Prototype]]` link. Methods are **delegated**, not copied, and the link can change at runtime. JS `class` is syntax sugar over prototypes.

| | Classical | Prototypal (JS) |
|---|---|---|
| Inherits from | Classes | Objects |
| Mechanism | Copy structure into instance | Delegate lookups via chain |
| When set | Compile time, static | Runtime, dynamic (can patch prototype) |
| Multiple inheritance | Interfaces / sometimes MI | Mixins, `Object.assign`, composition |
| Private state | Access modifiers | Closures, `#private` fields, WeakMap |

```js
class Animal {
  constructor(name) { this.name = name; }
  speak() { return `${this.name} makes a sound`; }
}
class Dog extends Animal {
  speak() { return `${super.speak()} — woof`; }
}
const d = new Dog("Rex");
console.log(d.speak());                                      // Rex makes a sound — woof
console.log(typeof Dog);                                     // function
console.log(Object.getPrototypeOf(Dog.prototype) === Animal.prototype); // true

// Live delegation: patching the prototype affects existing instances
Animal.prototype.sleep = function () { return `${this.name} sleeps`; };
console.log(d.sleep());                                      // Rex sleeps

// Pure prototypal style, no classes
const proto = { hello() { return "hi from " + this.n; } };
const o = Object.create(proto, { n: { value: "o" } });
console.log(o.hello());                                      // hi from o
```

- **Follow-up:** "Is JS `class` real classical OOP?" No. `class` gives you nicer syntax, `super`, strict mode, and constructors that throw without `new`, but underneath it is still prototype delegation.
- Common advice: favor composition over deep inheritance trees. NestJS DI is a composition example.

</details>

**28. What does `Object.create(null)` give you and when would you use it?**

<details>
<summary>Answer</summary>

It creates a truly empty object whose `[[Prototype]]` is `null`. It inherits nothing from `Object.prototype`: no `toString`, `hasOwnProperty`, `constructor`, or `__proto__` accessor. That makes it a safe "pure dictionary" for arbitrary string keys.

```js
const dict = Object.create(null);
dict["constructor"] = 1;
dict["__proto__"] = 2;                    // stored as a normal key, not a prototype change
console.log(Object.getPrototypeOf(dict)); // null
console.log(dict.__proto__);              // 2
console.log("toString" in dict);          // false
console.log(Object.keys(dict));           // [ 'constructor', '__proto__' ]
try { String(dict); } catch (e) { console.log(e.message); } // Cannot convert object to primitive value

const normal = {};
console.log("toString" in normal);        // true
console.log(normal["constructor"] === Object); // true  (inherited, surprise!)
```

When to use it:
- Lookup tables and caches keyed by user input (headers, query params, word counts), where keys like `"constructor"` or `"__proto__"` would otherwise clash with inherited members.
- Defending against **prototype pollution** when merging untrusted JSON.
- Libraries use it for internal maps (Node's `querystring` results, some template engines).

Trade-offs:
- `dict.hasOwnProperty(k)` doesn't exist, so use `Object.hasOwn(dict, k)`. You can't template-print it or `String()` it.
- For a real key-value store, a `Map` is usually better (any key type, `size`, ordered iteration). `Object.create(null)` is the lightweight option when you need a plain object, e.g. for JSON output.

</details>

**29. What is the difference between `Object.freeze()` and `Object.seal()`?**

<details>
<summary>Answer</summary>

Both stop you adding or deleting properties. `seal` still lets you **change existing values**. `freeze` makes every existing property **read-only** as well. Both are **shallow**: nested objects stay mutable.

| | Add props | Delete props | Modify values | Reconfigure |
|---|---|---|---|---|
| `Object.preventExtensions` | No | Yes | Yes | Yes |
| `Object.seal` | No | No | **Yes** | No |
| `Object.freeze` | No | No | **No** | No |

```js
"use strict"; // in sloppy mode these violations fail silently instead of throwing
const sealed = Object.seal({ a: 1, nested: { x: 1 } });
sealed.a = 2;                  // ✅ allowed
try { sealed.b = 3; } catch (e) { console.log(e.message); }  // Cannot add property b, object is not extensible
try { delete sealed.a; } catch (e) { console.log(e.message); } // Cannot delete property 'a' of #<Object>
console.log(sealed.a);         // 2

const frozen = Object.freeze({ a: 1, nested: { x: 1 } });
try { frozen.a = 2; } catch (e) { console.log(e.message); } // Cannot assign to read only property 'a' of object '#<Object>'
frozen.nested.x = 99;          // ✅ shallow! nested object still mutable
console.log(frozen.nested.x);  // 99
console.log(Object.isFrozen(frozen), Object.isSealed(frozen)); // true true

function deepFreeze(obj) {
  for (const v of Object.values(obj)) {
    if (v && typeof v === "object" && !Object.isFrozen(v)) deepFreeze(v);
  }
  return Object.freeze(obj);
}
const cfg = deepFreeze({ db: { port: 5432 } });
try { cfg.db.port = 1; } catch (e) { console.log(e.message); } // Cannot assign to read only property 'port' of object '#<Object>'
```

- **Pitfall:** In non-strict code, writes to frozen objects fail **silently**, which causes confusing bugs. ES modules and classes are always strict.
- **Pitfall:** `const` ≠ freeze. `const` only stops rebinding the variable.
- **Follow-up:** In TS, `as const` / `Readonly<T>` are compile-time only. `Object.freeze` is enforced at runtime. A frozen config object in NestJS is a common use.

</details>

**30. How do you deep clone an object in JavaScript? What are the limitations of `JSON.parse(JSON.stringify())`?**

<details>
<summary>Answer</summary>

Use the built-in **`structuredClone(obj)`** (browsers, Node 17+). It handles nested objects, `Date`, `Map`, `Set`, `RegExp`, typed arrays and circular references. `JSON.parse(JSON.stringify(obj))` only works for plain JSON-safe data. It drops, converts, or throws on almost everything else.

**`JSON.parse(JSON.stringify())` limitations:**

| Input | Result |
|---|---|
| `undefined`, functions, Symbol keys/values | Dropped (in arrays they become `null`) |
| `Date` | Becomes an ISO **string** |
| `NaN`, `Infinity` | `null` |
| `Map`, `Set`, `RegExp` | `{}` |
| Circular reference | Throws `TypeError` |
| `BigInt` | Throws `TypeError` |
| Class instances | Lose their prototype, become plain objects |

```js
const src = {
  date: new Date("2024-01-01T00:00:00Z"),
  undef: undefined,
  fn() {},
  nan: NaN,
  map: new Map([["k", 1]]),
  nested: { deep: [1, { x: 2 }] },
};
const viaJson = JSON.parse(JSON.stringify(src));
console.log(typeof viaJson.date, viaJson.nan, viaJson.map, "undef" in viaJson); // string null {} false

const { fn, ...cloneable } = src;        // structuredClone throws on functions
const viaSC = structuredClone(cloneable);
console.log(viaSC.date instanceof Date, viaSC.map.get("k"), viaSC.nan); // true 1 NaN
viaSC.nested.deep[1].x = 99;
console.log(src.nested.deep[1].x);       // 2  (truly deep)

const cyclic = { name: "a" };
cyclic.self = cyclic;
console.log(structuredClone(cyclic).self.name); // a
try { structuredClone({ f() {} }); } catch (e) { console.log(e.name); } // DataCloneError
```

`structuredClone` limitations: it throws on functions and DOM nodes, and it drops the prototype of class instances (you get plain objects) along with getters/setters.

**Manual deep clone (asked in machine-coding rounds):**

```js
function deepClone(value, seen = new WeakMap()) {
  if (value === null || typeof value !== "object") return value; // primitives & functions
  if (seen.has(value)) return seen.get(value);                    // handle cycles
  if (value instanceof Date) return new Date(value);
  if (value instanceof RegExp) return new RegExp(value.source, value.flags);
  if (value instanceof Map) {
    const m = new Map();
    seen.set(value, m);
    value.forEach((v, k) => m.set(deepClone(k, seen), deepClone(v, seen)));
    return m;
  }
  if (value instanceof Set) {
    const s = new Set();
    seen.set(value, s);
    value.forEach((v) => s.add(deepClone(v, seen)));
    return s;
  }
  const out = Array.isArray(value) ? [] : Object.create(Object.getPrototypeOf(value));
  seen.set(value, out);
  for (const key of Reflect.ownKeys(value)) out[key] = deepClone(value[key], seen); // incl. symbols
  return out;
}
const a = { d: new Date(0), list: [1, { x: 1 }], m: new Map([["k", { y: 1 }]]) };
a.self = a;
const b = deepClone(a);
b.list[1].x = 9;
console.log(a.list[1].x, b.self === b, b.d instanceof Date, b.m.get("k").y); // 1 true true 1
```

Walkthrough: return primitives as they are. The `WeakMap` records originals already cloned so that cycles resolve to the same copy. Special-case built-ins. Keep the prototype and recurse over all own keys. Time and space are O(n) in the number of nodes.

- **Pitfall:** Spread `...obj` and `Object.assign` are **shallow** copies.

</details>

**31. What is the difference between `for...in` and `for...of`?**

<details>
<summary>Answer</summary>

`for...in` iterates over **keys**: all enumerable string property names of an object, **including inherited ones**. `for...of` iterates over **values** of an **iterable** (arrays, strings, Map, Set, generators, NodeList) using `Symbol.iterator`. Use `for...of` for arrays. Use `for...in` (or better, `Object.keys`/`entries`) for plain objects.

| | `for...in` | `for...of` |
|---|---|---|
| Yields | Keys (always strings) | Values |
| Works on | Any object | Iterables only (plain objects throw) |
| Inherited props | Yes (enumerable ones) | N/A |
| Order | Integer keys ascending, then insertion order | Iterator's order |

```js
const arr = ["a", "b"];
arr.extra = "x";
Array.prototype.polluted = "p"; // someone patched the prototype

for (const k in arr) console.log(k);   // 0, 1, extra, polluted  (string keys!)
for (const v of arr) console.log(v);   // a, b

delete Array.prototype.polluted;

const user = { name: "Asha", age: 25 };
for (const k in user) console.log(k);  // name, age
try {
  for (const v of user) console.log(v);
} catch (e) {
  console.log(e.message);              // user is not iterable
}
for (const [k, v] of Object.entries(user)) console.log(k, v); // name Asha / age 25
for (const ch of "hi") console.log(ch);  // h, i
```

- **Pitfall:** `for...in` over an array gives string indexes (`"0" + 1 === "01"`) and picks up extra or inherited properties. Avoid it for arrays.
- Both support `break`/`continue`, unlike `forEach`. `for...of` also works with `await` (`for await...of`).

</details>

**32. Explain the Map vs Object trade-offs. When would you choose Map?**

<details>
<summary>Answer</summary>

Choose a `Map` for a **dynamic key-value collection**: keys added and removed at runtime, non-string keys, frequent iteration, or a need for `size`. Use a plain object for **fixed-shape records / structs** and anything you'll serialize to JSON.

| | `Object` | `Map` |
|---|---|---|
| Key types | string / symbol only (others coerced) | **Any** value, including objects and functions |
| Inherited keys | Yes (`constructor`, `toString`...) unless `Object.create(null)` | None |
| Order | Integer-like keys first, then insertion | Pure insertion order |
| Size | `Object.keys(o).length`, O(n) | `map.size`, O(1) |
| Iteration | Via `Object.keys/entries` | Directly iterable |
| Frequent add/delete | `delete` can de-optimize the object's hidden class | Optimized for it |
| JSON | Native | Needs `Object.fromEntries` / custom |
| Syntax / destructuring | Literal, `obj.x`, `{ ...o }` | `get`/`set` |

```js
const objKey = { id: 1 };
const m = new Map();
m.set(objKey, "user-1").set(1, "number one").set("1", "string one");
console.log(m.get(objKey), m.get(1), m.get("1"), m.size); // user-1 number one string one 3

const o = {};
o[objKey] = "user-1";
o[1] = "number one";
o["1"] = "string one";      // overwrites o[1]: keys are coerced to strings
console.log(Object.keys(o)); // [ '1', '[object Object]' ]

const ordered = { b: 1, 2: "x", a: 2, 1: "y" };
console.log(Object.keys(ordered)); // [ '1', '2', 'b', 'a' ]  integer keys jump ahead
console.log([...new Map([["b", 1], [2, "x"], ["a", 2], [1, "y"]]).keys()]); // [ 'b', 2, 'a', 1 ]

console.log(JSON.stringify(m));    // {}  (gotcha)
console.log(JSON.stringify(Object.fromEntries(new Map([["a", 1]])))); // {"a":1}
```

Pick a Map for: caches/memoization keyed by objects, LRU caches (insertion order plus `delete`/re-`set`), counting frequencies over user-supplied keys, and grouping (`Map.groupBy`).

</details>

**33. What is a WeakMap? How is it different from a Map?**

<details>
<summary>Answer</summary>

A `WeakMap` is a key-value store whose keys must be objects (or non-registered symbols) and are held **weakly**. If nothing else references a key object, the garbage collector can remove it along with its value. Because entries can disappear at any time, a WeakMap is **not iterable** and has no `size` and no `clear`. You only get `get`, `set`, `has` and `delete`.

| | `Map` | `WeakMap` |
|---|---|---|
| Key types | Anything | Objects (and non-registered symbols) only |
| Holds keys | Strongly (prevents GC) | Weakly |
| Iterable / `size` / `clear` | Yes | No |
| Use case | General collections | Metadata attached to objects you don't own |

```js
// Private data per instance, cleaned up automatically when the instance is GC'd
const privates = new WeakMap();
class User {
  constructor(name, password) {
    this.name = name;
    privates.set(this, { password });
  }
  check(pw) { return privates.get(this).password === pw; }
}
const u = new User("Asha", "s3cret");
console.log(u.check("s3cret"), Object.keys(u)); // true [ 'name' ]

// Memoize by object identity without leaking memory
const cache = new WeakMap();
function expensive(obj) {
  if (cache.has(obj)) return cache.get(obj);
  const result = Object.keys(obj).length; // pretend heavy work
  cache.set(obj, result);
  return result;
}
console.log(expensive({ a: 1, b: 2 })); // 2

const wm = new WeakMap();
try { wm.set("str", 1); } catch (e) { console.log(e.message); } // Invalid value used as weak map key
console.log(wm.size, typeof wm.keys); // undefined undefined
```

Use cases: caching computed data per DOM node or request object, private fields (before `#private`), tracking visited objects in deep clone, and framework internals (Vue's reactivity map, React-style per-component metadata).

- **Follow-up:** `WeakSet` is the same idea for membership ("have I seen this object?"). `WeakRef`/`FinalizationRegistry` are the lower-level tools.
- **Pitfall:** A Map used as a cache keyed by request or DOM objects is a classic memory leak. That is the point to switch to WeakMap.

</details>

**34. What is a Symbol? Why would you use it as an object key?**

<details>
<summary>Answer</summary>

A `Symbol` is a primitive whose values are **guaranteed unique**. Two `Symbol("id")` calls are never equal. As object keys, symbols **can't collide** with string keys or with other code's symbols, and they're hidden from normal enumeration (`for...in`, `Object.keys`, `JSON.stringify`). That makes them good for attaching metadata or "protocol" hooks without clashing with other properties.

```js
const id = Symbol("id");
const id2 = Symbol("id");
console.log(id === id2);      // false  (every Symbol() is unique)

const user = { name: "Asha", [id]: 101 };
user.id = "external lib's id"; // no collision with the symbol key
console.log(user[id], user.id);        // 101 external lib's id
console.log(Object.keys(user));        // [ 'name', 'id' ]
console.log(JSON.stringify(user));     // {"name":"Asha","id":"external lib's id"}
console.log(Object.getOwnPropertySymbols(user)); // [ Symbol(id) ]

console.log(Symbol.for("app") === Symbol.for("app")); // true (global registry)

class Money {
  constructor(v) { this.v = v; }
  [Symbol.toPrimitive](hint) { return hint === "number" ? this.v : `₹${this.v}`; }
}
const m = new Money(500);
console.log(+m, `${m}`); // 500 ₹500
```

Why use them as keys:
1. **No name clashes.** Libraries can tag your objects safely (e.g. React's `$$typeof: Symbol.for('react.element')`).
2. **Customize language behavior** with well-known symbols: `Symbol.iterator` (for-of), `Symbol.asyncIterator`, `Symbol.toPrimitive`, `Symbol.hasInstance`, `Symbol.toStringTag`.
3. **Semi-hidden properties** that don't show up in serialization.

- **Pitfall:** Symbols are **not private**. `Object.getOwnPropertySymbols` and `Reflect.ownKeys` reveal them. For real privacy, use `#private` fields.
- **Follow-up:** `Symbol()` is not a constructor (`new Symbol()` throws). `Symbol.for(key)` returns a shared, registry-wide symbol.
- NestJS uses symbols (or strings) as DI injection tokens to avoid token name collisions.

</details>

**35. What is the Event Loop? Describe the difference between the Call Stack, Microtask Queue, and Macrotask Queue.**

<details>
<summary>Answer</summary>

JS runs on a single thread. The **event loop** is the mechanism that lets it do non-blocking async work. It repeatedly takes a task from the **macrotask queue**, runs it to completion on the **call stack**, and then **drains the entire microtask queue** before rendering (in browsers) or picking the next macrotask.

- **Call stack:** Where synchronous code runs, one frame per active function call (LIFO). While the stack is busy, nothing else runs. That is why a long loop freezes the UI.
- **Microtask queue:** High-priority callbacks such as promise `.then/catch/finally`, code after `await`, `queueMicrotask`, `MutationObserver`, and in Node `process.nextTick` (its own queue, run even earlier). It is **fully drained** after every macrotask, including microtasks queued while draining.
- **Macrotask (task) queue:** `setTimeout`, `setInterval`, I/O callbacks, UI events, `MessageChannel`, `setImmediate` (Node). **One** macrotask runs per loop iteration.

One loop iteration: run one macrotask → drain all microtasks → (browser) maybe render → repeat.

```js
console.log("1: sync start");

setTimeout(() => console.log("6: macrotask (setTimeout)"), 0);

Promise.resolve()
  .then(() => console.log("3: microtask (then)"))
  .then(() => console.log("5: microtask (chained then)"));

queueMicrotask(() => console.log("4: microtask (queueMicrotask)"));

console.log("2: sync end");
// Output is in numeric order: 1, 2, 3, 4, 5, 6
```

The Web APIs / libuv (timers, network, fs) do the waiting **outside** the JS thread and push callbacks into the queues when they're ready.

- **Follow-up:** In Node, the macrotask side is split into phases (timers → pending → poll → check (`setImmediate`) → close), with `nextTick` and promise microtasks drained between callbacks.
- **Pitfall:** A recursive microtask chain can starve the loop: timers and rendering never get a turn. See Q37.

</details>

**36. What is the order of execution between `setTimeout(fn, 0)`, a Promise `.then()`, and synchronous code?**

<details>
<summary>Answer</summary>

**Synchronous code first, then Promise `.then` (microtasks), then `setTimeout(fn, 0)` (macrotask).** `setTimeout(fn, 0)` means "after at least 0 ms, in a later macrotask". A macrotask can only run once the call stack is empty and the microtask queue is fully drained.

A typical interview puzzle:

```js
console.log("A");
setTimeout(() => {
  console.log("F");
  Promise.resolve().then(() => console.log("G"));
}, 0);
setTimeout(() => console.log("H"), 0);
Promise.resolve().then(() => {
  console.log("C");
  setTimeout(() => console.log("I"), 0);
});
(async () => {
  console.log("B");     // async fn body runs synchronously until the first await
  await null;
  console.log("D");     // rest of the function is a microtask
})();
Promise.resolve().then(() => console.log("E"));
console.log("B2");
// A B B2 C D E F G H I
```

Walkthrough:
1. **Sync:** `A`, `B` (async body before `await`), `B2`. Timers F/H are queued, and microtasks C, D, E are queued in that order.
2. **Microtasks drained:** `C` (queues timer I), `D`, `E`.
3. **Macrotask F:** logs `F` and queues microtask G. Microtasks are drained before the next timer, so `G` prints.
4. **Macrotask H**, then **macrotask I**.

- **Pitfall:** `setTimeout(fn, 0)` is not really 0 ms. Browsers clamp nested timers to at least 4 ms, and the callback waits for the stack plus all microtasks.
- **Pitfall:** Code inside `new Promise((res) => { ... })` (the executor) runs **synchronously**. Only the `.then` callbacks are async.

</details>

**37. What are microtasks vs macrotasks? Give examples of each.**

<details>
<summary>Answer</summary>

Both are queued callbacks, with different priority. **Microtasks** run right after the current script or task finishes, and **all** of them run (including ones added while draining) before anything else. **Macrotasks** are picked **one per event-loop turn**, and rendering and I/O can happen between them.

| Microtasks | Macrotasks |
|---|---|
| `Promise.then/catch/finally` | `setTimeout`, `setInterval` |
| Continuation after `await` | `setImmediate` (Node) |
| `queueMicrotask(fn)` | I/O callbacks (fs, network, DB drivers) |
| `MutationObserver` (browser) | UI events (click, keypress), `MessageChannel` |
| `process.nextTick` (Node, separate queue, runs **before** promise microtasks) | Script execution itself, `requestAnimationFrame`* |

*`requestAnimationFrame` runs in the render step, before paint. It is not strictly a macrotask, but it is scheduled separately from microtasks.

Node example (inside an I/O callback, so the order is deterministic):

```js
const fs = require("fs");
fs.readFile(__filename, () => {
  setTimeout(() => console.log("5: setTimeout"), 0);
  setImmediate(() => console.log("4: setImmediate"));   // check phase comes before timers here
  Promise.resolve().then(() => console.log("3: promise"));
  process.nextTick(() => console.log("2: nextTick"));   // runs before promise microtasks
  console.log("1: sync in I/O callback");
});
// 1, 2, 3, 4, 5
```

Starvation demo, showing that microtasks block macrotasks:

```js
let n = 0;
setTimeout(() => console.log("timeout finally ran after", n, "microtasks"), 0);
function spin() { if (++n < 100000) Promise.resolve().then(spin); }
spin();
// timeout finally ran after 100000 microtasks
```

- **Why it matters:** For heavy work, break it up with `setTimeout`/`setImmediate` (macrotasks) so I/O and rendering can run in between. Recursive `.then` or `nextTick` chains don't give them a turn.
- **Follow-up:** At the top level of a script, `setTimeout(0)` vs `setImmediate` order in Node is **non-deterministic**. Inside an I/O callback, `setImmediate` always runs first.

</details>

**38. What is a generator function? How does `yield` work?**

<details>
<summary>Answer</summary>

A generator (`function*`) is a function that can **pause and resume**. Calling it doesn't run the body. It returns a **generator object** (an iterator). Each `.next()` runs the body until the next `yield`, which pauses and hands out `{ value, done: false }`. A `return` (or reaching the end) gives `{ value, done: true }`. The value passed to `next(x)` becomes the result of the paused `yield` expression, so values can flow in both directions.

```js
function* idGen() {
  console.log("started");
  const reset = yield 1;      // pauses here; the value passed to next() lands in `reset`
  console.log("got", reset);
  yield 2;
  return "done";
}
const it = idGen();           // nothing runs yet
console.log(it.next());       // started, then { value: 1, done: false }
console.log(it.next("hi"));   // got hi, then { value: 2, done: false }
console.log(it.next());       // { value: 'done', done: true }
console.log(it.next());       // { value: undefined, done: true }

function* naturals() { let n = 1; while (true) yield n++; } // infinite, but lazy
function* take(iter, k) { for (const x of iter) { if (k-- <= 0) return; yield x; } }
console.log([...take(naturals(), 5)]); // [ 1, 2, 3, 4, 5 ]

function* inner() { yield "a"; yield "b"; }
function* outer() { yield 0; yield* inner(); yield 1; }    // yield* delegates
console.log([...outer()]); // [ 0, 'a', 'b', 1 ]
```

- Generators are both iterable and an iterator, so `for...of`, spread and destructuring work on them. Note that `for...of`/spread ignore the final `return` value.
- `it.return(v)` finishes the generator early (runs `finally` blocks). `it.throw(err)` throws an error at the paused `yield`.
- Uses: lazy/infinite sequences, pagination (`async function*` + `for await`), custom iterables, and **redux-saga**. Historically, `co` used generators to emulate `async/await`, which is essentially generators plus promises.
- **Pitfall:** Arrow functions can't be generators, and a generator object can only be consumed **once**.

</details>

**39. How do you make a custom iterable? What is `Symbol.iterator`?**

<details>
<summary>Answer</summary>

An object is **iterable** if it has a method at the key `Symbol.iterator` that returns an **iterator**: an object with a `next()` method returning `{ value, done }`. `Symbol.iterator` is the well-known symbol that `for...of`, spread `...`, destructuring, `Array.from`, `Promise.all` and `new Map/Set(...)` look up to get that iterator.

```js
class Range {
  constructor(from, to, step = 1) {
    this.from = from;
    this.to = to;
    this.step = step;
  }
  [Symbol.iterator]() {
    let current = this.from;
    const { to, step } = this;
    return {
      next() {
        if (current > to) return { value: undefined, done: true };
        const value = current;
        current += step;
        return { value, done: false };
      },
    };
  }
}
const r = new Range(1, 10, 3);
console.log([...r]);               // [ 1, 4, 7, 10 ]
for (const n of r) console.log(n); // 1 4 7 10  (fresh iterator each time → re-iterable)
const [first, second] = r;
console.log(first, second);        // 1 4
console.log(Math.max(...r));       // 10

// Same thing, shorter, with a generator
const range2 = {
  from: 1,
  to: 3,
  *[Symbol.iterator]() {
    for (let i = this.from; i <= this.to; i++) yield i;
  },
};
console.log(Array.from(range2)); // [ 1, 2, 3 ]
```

Walkthrough: each call to `[Symbol.iterator]()` creates a new iterator with its own `current`, so the `Range` can be iterated many times. The iterator's closure holds the cursor, and `done: true` tells the consumer to stop.

- **Iterable vs iterator:** An iterable *produces* iterators. An iterator *is* the cursor. Generator objects are both (their `[Symbol.iterator]` returns `this`), which is why they can be consumed only once.
- Optional `return()` on the iterator is called on early exit (`break`, destructuring fewer items), which is useful for cleanup.
- **Follow-up:** `Symbol.asyncIterator` + `async *[Symbol.asyncIterator]()` gives `for await...of`, e.g. for streaming paginated API results or Node streams.

</details>

**40. What is the difference between `Promise.all`, `Promise.allSettled`, `Promise.race`, and `Promise.any`?**

<details>
<summary>Answer</summary>

All four take an iterable of promises and run them concurrently. They differ in **when they settle and with what**:

| Method | Resolves when | Rejects when | Result |
|---|---|---|---|
| `Promise.all` | **All** fulfill | **First** rejection (fail-fast) | Array of values, in input order |
| `Promise.allSettled` | All settle (never rejects) | Never | Array of `{ status, value }` / `{ status, reason }` |
| `Promise.race` | First to **settle** fulfills | First to settle rejects | That first value / reason |
| `Promise.any` | First to **fulfill** | **All** reject | First value, or an `AggregateError` with `.errors` |

```js
const ok = (v, ms) => new Promise((res) => setTimeout(() => res(v), ms));
const fail = (msg, ms) => new Promise((_, rej) => setTimeout(() => rej(new Error(msg)), ms));

(async () => {
  console.log(await Promise.all([ok("a", 20), ok("b", 10)])); // [ 'a', 'b' ]  (input order kept)
  await Promise.all([ok("a", 20), fail("boom", 10)]).catch((e) => console.log("all:", e.message)); // all: boom

  const settled = await Promise.allSettled([ok("a", 10), fail("boom", 5)]);
  console.log(settled.map((s) => s.status)); // [ 'fulfilled', 'rejected' ]

  await Promise.race([ok("slow", 20), fail("fast-fail", 5)]).catch((e) => console.log("race:", e.message)); // race: fast-fail

  console.log("any:", await Promise.any([fail("x", 5), ok("first-ok", 15), ok("later", 25)])); // any: first-ok
  await Promise.any([fail("x", 5), fail("y", 10)]).catch((e) =>
    console.log(e.constructor.name, e.errors.map((er) => er.message)) // AggregateError [ 'x', 'y' ]
  );
})();
```

When to use each:
- **`all`:** Independent calls where you need every result, e.g. loading a dashboard (`user`, `orders`, `stats`) in parallel.
- **`allSettled`:** Batch jobs where partial failure is fine, e.g. sending 100 notifications and reporting which ones failed.
- **`race`:** Timeouts: `Promise.race([fetchData(), timeout(5000)])`.
- **`any`:** Redundancy, e.g. querying several mirrors or CDNs and taking the first success.

- **Pitfall:** `Promise.all` doesn't **cancel** the other promises on failure. They keep running, and their results are simply ignored. Use `AbortController` if you need cancellation.
- **Pitfall:** Empty input: `all([])` / `allSettled([])` resolve to `[]` immediately, `any([])` rejects with `AggregateError`, and `race([])` stays pending forever.
- **Follow-up:** Running 1,000 requests through `Promise.all` fires them all at once. Use a concurrency limiter (p-limit or batching) instead.

</details>
