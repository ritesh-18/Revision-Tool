<!-- page 18 -->

> Question (top margin): What is cutting-edge technology? E.g. gRPC.

## Async-Await

### `Promise.resolve()`

- `Promise.resolve()` is a static method that resolves a given value to a promise.
- If the value is a promise, that promise is returned.
- If the value is a "thenable", `Promise.resolve()` will call the `then()` method with two callbacks it prepared; otherwise the returned promise will be fulfilled with the value.

```js
let x = Promise.resolve(123);
x.then((val) => { console.log(val); }); // 123
```

- This `then()` also returns a promise, but with value `undefined`, because we are not returning anything from this `then()`.

### `Promise.reject()`

- A static method that returns a promise object that is rejected with a given reason.

### Queues

- Promise callbacks go to the **microtask queue**.
- Normal callbacks (e.g. `setTimeout`) go to the **event queue** (task / callback queue).
- The microtask queue has higher priority.

### Why async/await?

- Because of `.then()` and `.catch()` chains, we are again creating a "promise hell".
- How do we resolve it? With **async-await**.

## async & await

1. We can declare a function `async`.
2. If you declare a function `async`, it does the following:
   - (a) It allows the use of the `await` keyword.
   - (b) It allows consuming a promise using `await`.
   - (c) An async function always converts your return value to a promise.

<!-- page 19 -->

```js
async function fx() {
  const data = await fetch(url);
  return data;
}
```

1. `.then()` is a method of a promise. It does **not** block execution — it registers a callback to run when the promise is resolved. Code after `.then()` keeps running immediately.
2. `await` is used inside an async function. It pauses the execution of that function until the promise is resolved or rejected. Code after `await` runs only after the promise settles.
3. The order of logs (function execution) can change depending on whether you use `.then()` or `await`.
   - Only a purely sync operation will block.
   - If it is an async operation — e.g. creating a promise is sync, but resolving/rejecting it is async (with `setTimeout`) — at this point it returns a promise with an `undefined` value and `pending` state, and then starts executing the other lines of code.
- Inside an async function things look sync, but overall it is async.

Example (the numbers in the notes mark the order of the output):

```js
function fetchData(url) {
  return new Promise(function (res, rej) { // executor runs synchronously
    console.log("Started downloading", url);          // (2)
    setTimeout(function processDownloading() {
      let data = "dummy data";
      console.log("Download completed");              // (4)
      res(data);
    }, 7000);
  });
}

console.log("Start");                                 // (1)
let promiseObj = fetchData("url");
promiseObj.then(function A(val) { console.log(val); }); // (5)
console.log("End");                                   // (3)
```

Output order: `Start` → `Started downloading url` → `End` → `Download completed` → `dummy data`.

<!-- page 20 -->

> Note (top): But under the hood async-await works differently — iterators and generators are used under the hood.

## Lecture: async-await (2nd part)

```js
async function fn() {
  const res1 = await call1();
  console.log("processing data");
  const res2 = await call2();
}
```

When you call `fn()`, what happens step by step:

1. `fn()` starts → `await call1()` runs and returns a promise (data: `undefined`, status: `pending`).
2. It immediately saves the rest of the function and exits to handle other things.
3. Later, when `call1()` resolves, JS resumes the saved function with `res1` → `console.log()` → `await call2()` again returns a promise and waits.
4. When `call2()` resolves, it resumes and finishes the function.

Code:

```js
function fn() {
  return new Promise((res, rej) => {
    setTimeout(function () {
      console.log("Promise executing");
      res(123);
    }, 5000);
  });
}

let x = fn();

x.then((data) => {
  console.log("value of promise is", data); // 123
  return 200;
});

x.then((data) => {
  console.log("value of promise is", data); // 123
});
```

- Diagram: the promise object is drawn as `{ status, value, onFulfillment: [anon, anon], onRejected: [] }`. Each `x.then(...)` call pushes its (anonymous) callback into the `onFulfillment` array, so both callbacks receive the same value `123`.

<!-- page 21 -->

- But if you do:

```js
x.then((d) => { return 100; }) // returns a new promise
 .then((d) => { console.log(d); }); // here you will get 100 (not 123)
```

- Q: What is the use of the previous logic (attaching multiple `.then()` to the same promise)?
  - Ans: Sometimes we need to apply different logic to the same data; then we can do it without creating an extra variable (which would store the first data and then do the operations).

### Conversion to promise

- If the value (after `await`) is not a promise, it converts the value to a resolved promise and waits for it. The awaited value's identity does not change as long as it does not have a `then` property that is callable.

```js
async function fn() {
  const y = await 20;
  console.log(y); // 20

  let obj = {};
  console.log((await obj) === obj); // true
}
fn();
```

### Async-Await Hell

```js
async function fx() {
  const res1 = await p1();
  const res2 = await p2();
  const res3 = await p3();
}
```

- This is known as "async-await hell" (each call waits for the previous one, even if they are independent).
- How to resolve this?
  - `Promise.all()`
  - `Promise.allSettled()`
  - `Promise.any()`

1. `Promise.all()` → takes an iterable of promises as input and returns a single promise. The returned promise fulfills when all of the input promises fulfill (including when an empty iterable is passed), with an array of the fulfillment values.
   - It rejects when any of the input promises rejects.

<!-- page 22 -->

```js
Promise.all([pr1, pr2, pr3 /* ... */])  // returns another promise
  .then((val) => console.log(val))      // output: array of outputs, in order
  .catch((err) => console.log(err));
```

- Each promise executes in parallel, but the final result comes once all get resolved, or as soon as any one gets rejected.

### Q. How to do chaining?

- When the 3rd promise's data depends on the 2nd promise, and the 2nd on the 1st, you can simply bind them in a function and call that function inside `Promise.all([fx()])`.

```js
async function fx() {
  const res1 = await p1();
  const res2 = await p2(res1);
  const res3 = await p3(res2);
  return res3;
}
// bind them in an async function and call that function
Promise.all([fx()]);
```

2. `Promise.any()` — it also takes an array of promises and returns the fulfilled value as soon as any one of them gets fulfilled, and gets rejected when every one gets rejected.
   - But how do we know which promise resolved first?

3. `Promise.allSettled()` — same as `Promise.all()`, but it returns all the results (failed/rejected or fulfilled), and it waits for everyone to be either resolved or rejected; only then does it return. (You will get an array of values — one per promise.)

<!-- page 23 -->

## How to handle errors in JS

### `throw`

- The `throw` statement throws a user-defined exception. Execution of the current function will stop (the statements after `throw` won't be executed), and control will be passed to the first `catch` block in the call stack. If no `catch` block exists among the caller functions, the program will terminate.

```js
function fn() {
  if (err) {
    throw "Something went wrong";
  }
}

try {
  fn();
} catch (err) {
  console.log(err); // or console.error(err)
  // e.g. "Parameter is not a number"
}
```

### Handling errors with promises

```js
// If there is an error, the second callback will be called
res.then(
  (d) => { console.log(d); },
  function (error) { console.log(error); }
);

// or
res.then((d) => {}).catch((err) => {});

// or
res.then((d) => {}, errFx).then().catch();
```

- In the last form: if there is an error, `errFx` executes (and handles it); the later `.catch()` executes only if an error still occurs after that — otherwise it is not executed.

<!-- page 24 -->

### `finally()` method

- `finally()` is a method of a promise: it schedules a function (the callback function) to be called when the promise is settled. Like `then()` and `catch()`, it immediately returns an equivalent Promise object, allowing you to chain calls to other promise methods — an operation called **composition**.

```js
.finally(() => {}); // it always executes — whether success or rejected
```

### Error-first callback

- The first argument of the callback is reserved for an error object. If an error occurred, it will be returned via the first `err` argument.
- Similarly, the second argument is reserved for any successful response data. If no error occurred, `err` will be set to `null` and any successful data will be returned in the second argument.

```js
fs.readFile("abc.txt", function (err, data) {
  // code
});
```

- It's a coding style.

```js
function fetchData(url, fn) {
  // processing
  console.log(data);
  fn(err, res); // here fetchData will pass (err / data)
}

function fn(err, res) {
  if (err) { /* handle error */ }
  return res;
}

fetchData("url", fn);
```

<!-- page 25 -->

## Lecture: Generators & Iterators (Advanced Concept) — (M. Imp)

### Iterators

- It is a general programming term (exists in multiple languages, e.g. Python, C++, etc.).
- It is a design pattern: a **behavioural design pattern** that lets you traverse elements of a collection without exposing its underlying representation (e.g. stack, queue, etc.).

Programming languages (diagram — a tree splitting into two):

- **Declarative languages** — we define *what* to do and don't care about the *how*. E.g. React.
- **Imperative languages** — we manually define how to achieve something (manual logic).

Example: print the elements of an array.

- Imperative way:

```js
for (let i = 0; i < arr.length; i++) {
  console.log(arr[i]);
}
```

- Declarative way — requirement: we do not want to fetch all elements at the same time; whenever we want, we should be able to get the next value (index).

```js
function fetchNewElement(arr) {
  let index = 0;
  function returnNext() {
    const val = arr[index];
    index++;
    return val;
  }
  return returnNext;
}

const autoFetcher = fetchNewElement([1, 2, 3, 4]); // contains a function
console.log(autoFetcher()); // 1
console.log(autoFetcher()); // 2
```

- Using the closure property, we are accessing the `index` variable.

<!-- page 26 -->

> Question (top margin): How to write your own function (or mechanism) like async-await?

- You can add one edge condition (index not possible):

```js
if (index >= arr.length || index < 0) {
  return undefined;
}
```

- NOTE: This is the **imperative** way to create iterators.

### How to use an iterator

```js
const arr = [1, 2, 3, 4, 5];
const it = arr[Symbol.iterator](); // now an Array Iterator: an object with a next() method

console.log(it.next()); // { value: 1, done: false }
console.log(it.next()); // { value: 2, done: false }
```

An iterator result has:

- `next()` → call it for the next available result `{ value, done }`.
- `value` → shows the next fetched value.
- `done` → `false` means more elements exist; `true` means no element is left.

(Note: in the notebook `value()` and `done()` are written like methods — they are actually properties of the result object.)

- [MDN] An iterator object is an object that conforms to the iterator protocol by providing a `next()` method that returns an iterator result object.
- **Iterable** — the iterable protocol allows JavaScript objects to define or customize their iteration behaviour.
  - E.g. arrays are iterable, meaning arrays follow the iterable protocol.
  - Objects are not iterable directly.

### How to make a fully declarative "fetchNextElement"?

- Solution: using **generators**. How? Generators are special functions — they can be paused and resumed, allowing you to produce (or generate) a sequence of values over time, instead of computing them all at once.

<!-- page 27 -->

> Question (top margin): How to use the debugger?

- Declarative approach (we are not writing our own logic):

```js
function* newGenerator() {  // it executes differently
  yield 100;
  yield 55;
  yield -1;
}

const it = newGenerator();
it.next(); // → 100   output: { value: 100, done: false }
it.next(); // → 55
```

- If the generator is written as below, both lines will execute on the first `next()` — it executes until the next `yield`:

```js
console.log("Inside Generator");
yield 100;
```

### How does it work?

1. `function*` defines a generator function.
2. Inside, you use the `yield` keyword to "pause" and return a value.
3. Calling the generator function returns a generator object.
4. You use `.next()` to get the next value (after executing up to the first `yield`, it moves out of the call stack).

```js
function* gen(arr) {
  for (let i = 0; i < arr.length; i++) {
    yield arr[i];
  }
}

const it = gen(arr);
it.next(); // → 1, 2, 3, 4, ... on successive calls
```

- You can yield any type of data (even a function).

### Passing arguments to `next()`

- You can also pass an argument in `next()`.

```js
function* fx() {
  const x = yield 10; // 1st execution: stops here and returns 10
  const y = x + 10;   // 2nd execution (x = 20)
  yield y;            // output → { value: 30 }
}

const it = fx();
it.next();   // → { value: 10, done: false }
it.next(20); // in this line x = 20 is assigned; → { value: 30, done: false }
```

- `const x = yield 10;` — this much only executes during the first `next()`; the assignment to `x` happens on the next call.

<!-- page 28 -->

> Note (top): A generator object is returned by a generator function, and it conforms to both the iterable protocol and the iterator protocol. Generator is a subclass of the hidden Iterator class.

### Can we use the `return` keyword?

- Yes. But `return 44` means a final result `{ value: 44, done: true }`.

```js
function* fx() {
  yield 10;   // 1st iteration:  { value: 10, done: false }
  return 44;  // 2nd iteration:  { value: 44, done: true }
  yield 20;   // 3rd iteration:  { value: undefined, done: true }
}
```

- The last value should come from `yield` — do not pass it via `return` (anything after `return` is never reached).

### Generator with promise

```js
function* execute() {
  yield new Promise((res, rej) => {
    res(10);
  });
}

const it = execute();
it.next(); // → { value: Promise, done: false }  — how to resolve it?
it.next().value.then(/* ... */);
```

- If you want to execute multiple promises (and also support chaining), you can do it easily by writing a generator function.

```js
function* execute() {
  const downloadData = yield download("url");
  const writeData = yield writeFile(downloadData);
  // ...
}

const it = execute();
```

<!-- page 29 -->

> Top label: [fetch/Axios API] [illegible — boxed heading]

- Note: use `it.next().value` (not `it.value.next`).

```js
const ft = it.next(); // → { value: Promise, done: false }

ft.value.then(function doAfterReceiving(val) {
  console.log("....", val);
  // if (ft.done) return;   // (crossed out in notes) no more yields
  const futVal = it.next(val);
  if (futVal.done) return;
  futVal.value.then(doAfterReceiving); // recursion
});
```

- The above code is basically async-await → instead of this, you can use async-await:

```js
async function fn() {
  // instead of yield, replace it with the 'await' keyword
}
```

- And there is no need to define iterators and `next()`. — Declarative approach.

(P.T.O.)

<!-- page 30 -->

## Let's talk about Objects (more things)

### Important Object methods

1. How to get (list) the keys of an object (keys are unique in an object):

```js
Object.keys(obj1); // → array of keys (strings)
```

2. How to fetch all values of an object:

```js
Object.values(obj1); // → ["...", ...] array of values
```

3. How to get key:value pairs in array format:

```js
Object.entries(obj1);
// output: [["name", "xyz"], ["age", 22]]
```

4. How can we check the number of key:value pairs in an object?

```js
Object.keys(obj).length;
```

## Mutability and Immutability in JS Objects

What is mutable:

```js
let x = 10;
x = 9;
```

- Here we are able to update the value of `x`; this mechanism of being able to update a variable's value is called **mutability**.
- If we are not able to modify the value, then it is **immutable**.

Immutable:

```js
const x = 10;
x = 9; // not allowed
```

- `const` is used to make them immutable.
- But this does not happen with objects/arrays. Why? Because internally we are storing the array's pointer (reference) value, but we can still update the values inside the array/object.

<!-- page 31 -->

```js
const a; // not allowed — you have to give some value
// SyntaxError: Missing initializer in const declaration
```

### Q. Why do we need immutability?

- There are a lot of places in programming where immutability becomes extremely important.
- E.g. a DB connection configuration (value): most of the time (more or less) we do not want to update the configuration of this DB connection. In this type of scenario immutability is required.

### `const` with objects

- If we have a `const`-based init for objects (arrays), it does not make the object fully immutable.
- Diagram: the variable `obj` lives on the **stack**, the object `{ name: "ritesh" }` lives in the **heap**.

```js
const obj = { name: "ritesh" };
obj.name = "sonu"; // modified — allowed, so not immutable
```

- Here `const` restricts the reassignment of the variable.

```js
const obj = {};
obj = {};          // not allowed
obj = { age: 20 }; // also not allowed — reassigning to a new object is not allowed
```

- A new reference is not allowed in `const`.
- So technically, `const` objects are not fully immutable.

### Q. How to make an object fully immutable?

- Yes, we can make it fully immutable:
  - `Object.seal()`
  - `Object.freeze()`

(P.T.O.)

<!-- page 32 -->

1. `Object.freeze()`  2. `Object.seal()`

- Using these two methods we can achieve the immutability property.

### `Object.seal(obj)`

- Restricts adding new key:value pairs and deleting existing key:value pairs.
  - `delete obj.age` → `false`
  - `obj.phone = ...` → not allowed
- But you can update the value of an existing key.

```js
const obj = { name: "abc" };
Object.seal(obj);
obj.name = "ritesh"; // allowed
obj.age = 23;        // not allowed
delete obj.name;     // not allowed
```

### `Object.freeze(obj)`

- Here you can't even update the existing key:value.

```js
const obj = { name: "abc" };
Object.freeze(obj);
obj.name = "ritesh"; // update — not allowed
obj.age = 23;        // add — not allowed
delete obj.name;     // delete — not allowed
```

- This provides the highest level of immutability; it creates a frozen object.

### Checking

- `Object.isFrozen(obj)` → `true` / `false` (either frozen or not).
- `Object.isSealed(obj)` → `true` if sealed — even a frozen object gives `true`; `false` for all other cases.

### Q. Half-seal properties

- `Object.preventExtensions(x)` — similar to seal, but it allows deleting existing (key, value) pairs.

<!-- page 33 -->

### `Object.defineProperty()`

- You can add prevention (control) — e.g. not writable (read-only) — at the key level.

```js
Object.defineProperty(obj, "name", { writable: false });
obj.name = "ram"; // it will not update
```

- So for frozen objects, internally it uses `defineProperty()`.
- `{ configurable: false }` → you cannot delete the key.
- You can pass multiple configs: `{ configurable: false, writable: false }`.

### Q. Can we make our own `Object.seal()`?

- Yes. How?
  - Using `Object.preventExtensions()` → similar to seal, but allows delete.
  - `Object.defineProperty()` with `{ configurable: false }` → restricts deletion (and with `writable: false` as well → that makes it `Object.freeze()`).
  - Together (`configurable: false` + `preventExtensions`) → makes `Object.seal()`.

```js
function customSeal(obj) {
  let keys = Object.keys(obj);
  for (let i = 0; i < keys.length; i++) {
    Object.defineProperty(obj, keys[i], { configurable: false });
    // if you add writable: false as well → frozen()
  }
  Object.preventExtensions(obj);
}
```
