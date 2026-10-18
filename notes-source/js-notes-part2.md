<!-- page 25 -->

## (continued) Scope and the Two Phases of Execution

> Side note: "`use strict`" is also important.

### Q1. `var` inside an `if` block

```js
var x = 10;
console.log(x); // 10

if (true) {
  var x = 20;
  var y = 30;
  console.log(x, y); // 20 30
}

console.log(x, y); // 20 30
```

- In the 1st phase (memory creation), `x` and `y` both live in the global scope (`var` is not block-scoped). In the 2nd phase (execution) `x` goes 10 → 20 and `y` gets 30.
- Why does the first log print 10? Because the modification happens on a later line.
- If you put `console.log(x, y)` **before** the `if` block: in the 1st phase `y` is already defined, but its value is `undefined`, so the output is `10 undefined`.

### Note: Strict mode

- Since "auto-global" (assigning to an undeclared variable creates a global) is a flaw of JS, if you want to avoid this you can block it with:
  - `"use strict"` → strict mode
  - Without `"use strict"` → sloppy mode

### Q2. `var` inside a function vs. global `var`

```js
var x = 20;

function fun() {
  var x = 20;
  console.log(x); // 20
}

var x = 30; // no redeclaration in phase 2 – only updating the global `x`

fun();
console.log(x); // 30 – because of the initialization to 30
```

- Global scope: `x` = 20 → 30. Function scope: its own `x` = 20.
- The function prints 20 because of the function's own `x`; the global `var x = 30` is not a redeclaration, only an update.

### Q3. `var` in a `for` loop

```js
var x = 30;                          // (i)
for (var x = 1; x < 3; x++) {        // (ii)
  console.log(x);
}
console.log(x);                      // (iii)
```

- In lines (i) and (ii) there is no (new) redeclaration — `var` in the `for` loop does not create a separate block scope; it is the same global `x`.
- Phase 2: `x = 30` → updated to `x = 1` because of the `for` loop → prints `1, 2` → then updated to `3`.
- Output:
  - `1, 2` → from the `for` loop
  - `3` → from the last `console.log`

<!-- page 26 -->

> Side note: [Airbnb JS config — GitHub code]

- Redeclaration of a `var` variable happens only when it is in function scope; if it is block scope, there is no (separate) redeclaration of the `var` variable.

## `let` / `const` — Block Scope

- Both work in a similar way when we talk about them from a scope perspective.
- Whenever we declare a variable with `let`, the variable gets the scope of the **nearest block**:
  - If the nearest block is a `for` loop block → `for` loop scope.
  - If the nearest block is an `if`/`else` → the variable gets the scope of the `if`/`else`.
  - If the nearest block is a function block → the variable gets a block scope inside the function.

### What does "block scope inside a function" mean, and how is it different from `var` function scope?

- When we say **function scope**, it means that no matter where we declare the variable in the function, it is available throughout the function.
- That is not the case with **block scope inside a function**. In a block scope, variables are only accessible **after** they are declared; we can't access them before their declaration.

```js
function fx() {
  console.log(x); // ReferenceError (TDZ – temporal dead zone)
  let x = 10;
}

// but

function fx2() {
  console.log(x); // no error (prints undefined)
  var x = 10;
}
```

### Temporal Dead Zone (TDZ)

- The place before the declaration of a block-scoped variable, where we are trying to use that variable inside a block — because of the ReferenceError we are not able to run the code — that place is known as the **TDZ**.
- In a block-scoped variable, we cannot access the variable before its initialization. This makes block-scoped variables special.

<!-- page 27 -->

> Side notes at top of page: `const` can't be left undefined (a `const` must be assigned a value where it is declared) [partly illegible]. Stack pointer, code pointer → in process. Applies to (`let`, `const`, `class`).

- The region before the declaration of the block-scoped variable is called the **Temporal Dead Zone**.

### No redeclaration with `let`

```js
let x = 10; // block scope in the global area
let x = 30; // compile-time error – you can't re-declare inside a block scope
```

- `let` does not allow redeclaration of a variable in block scope (caught in phase 1).

```js
var x = 20;
let x = 10; // compile-time error – in the global scope x is already declared
            // (let is block-scoped, yes, but here it is inside the global scope)

// or

let x = 20;
var x = 10; // also an error
```

## Hoisting

- Hoisting is the **consequence of the scoping mechanism** of JS.
- Because JS executes your code in two phases, a lot of variables are already known in phase 1, and they are accessed in phase 2. So it looks to a lot of people like JS knows about a few variables before their declaration.
- And indeed it is true, because in phase 1 all the formal declarations are processed, so JS indeed knows about the variables before the execution phase.
- This mechanism of knowing variables before their declaration line is termed **hoisting**. This word is not actually present in the ECMAScript docs; the JS community came up with this one-word definition for this consequence.
- For `function`, `function*`, `async function` and `async function*` we are able to get the actual value before initialization (this comes under "type 1" behaviour, per MDN naming).

## Function Expression

- (1) `function abc() {}` — a function declaration.
- Functions are first-class citizens in JS.
- How to declare a function — using the `function` keyword.
- We can store a function in a variable:

```js
const data = function () {}; // function expression
// vs. a function declaration: function data() {}
```

<!-- page 28 -->

## (continued) Function Expression

- Here we are creating a function, but the first valid token is `const`, not `function`. Hence we call this type of instruction a **"function expression"**.
- There are many ways to define a function expression:

```js
const val = function fx() {};  // named function expression
const val2 = function () {};   // anonymous function expression
const val3 = () => {};         // arrow function expression
(() => {})();                  // IIFE (Immediately Invoked Function Expression)
(function () {})();            // IIFE, etc.
```

### Each type of function expression

- Difference between named and anonymous function expressions:
  - **Named** → a name has been attached.
  - **Anonymous** → no name is attached.

**Use case:** a function expression can be used to pass a function as an argument to another function.

```js
function fx(sum) {}
let sum = () => {};
fx(sum);
```

**Should we use a named function expression or an anonymous function expression?**

- **Ans:** In a recursion program, anonymous functions are hard to use, whereas a named function expression can be easily integrated into a recursive environment.
- If we want to calculate the factorial of each element of an array using `map()`, then we are bound to use a named function expression.

<!-- page 29 -->

```js
array.map(function fac(ele) {
  if (ele === 1) return 1;
  return ele * fac(ele - 1);
});
```

### Deprecated feature: `arguments.callee`

- `arguments.callee` could be used to apply recursion on an anonymous function (not recommended). `arguments` is a keyword here.

```js
arr.map(function (n) {
  if (n === 1) return 1;
  return arguments.callee(n - 1) * n;
});
```

### Anonymous functions are hard to debug

- When you check the call stack of the function, you will not find any name for an anonymous function expression.
- `console.trace()`: a static method that outputs a stack trace to the console.

```js
function fx1() {
  let arr = [1, 2, 3, 4, 5];
  const result = fx2(arr);
}

const fx2 = function (arr) {
  console.log("fx called");
  console.trace("callstack");
};
```

## Arrow Function

- Same as an anonymous function; this function expression is generally preferred for its concise syntax.
- There is one very fundamental difference between an arrow function and other function expressions: in an arrow function the `this` keyword is resolved **lexically**, whereas in others the `this` keyword is resolved by the **call site**.

<!-- page 30 -->

### Some points regarding arrow functions

- If it is one line of code, then there is no need to write the `return` keyword.
- If only one parameter is there, then no need to use parentheses.

```js
x => x * x; // an arrow one-line function
```

## IIFE (Immediately Invoked Function Expression)

- A function expression that is called the moment we define it is called an IIFE.

```js
(function () { console.log("x"); })();

// or – wrapper parentheses around the function, then a subsequent pair of parentheses to call it
(function square(x) { console.log(x * x); })(2); // 2 * 2 = 4 (output)
```

- Once we have prepared the IIFE and called it, after that we can never use it again, because the IIFE gets wiped off from memory once the execution is done.
- IIFEs can be very useful to avoid name conflicts, because they don't conflict with variables that are in outer scopes.
- IIFEs can be useful for scoped / temporary logic as well.

<!-- page 31 -->

## Use of Object-Oriented Structure in JS

- Object is one of the strongest types in JS.
- In software engineering, anything that we have can be mapped to a blueprint or a vision. For example, in Amazon every product has a similar structure; we can generalize this and make sure we don't repeat anything again and again.
- **Classes:** a blueprint of a set of real-life entities.
- **Objects:** using classes, the final entity that we will develop is the object.
- Classes represent how an entity should **look** and **behave**:
  - "How they look" refers to the **properties** they possess.
  - "How they behave" means what **actions** can be performed on them.
- Example — Product class:
  - Properties → name, price, company, expiry, etc.
  - Behaviour / actions → buy, display details, rate a product, add to cart, etc.
- Class →
  - data members (properties)
  - member functions (behaviour / actions)

### How to make a class in JS?

- Using the `class` keyword, and include the data members and member functions inside it.

```js
class NameOfTheClass {
  // you can add details like member functions & data members
}
```

Basic example:

```js
class Product {
  name; price; expiryDate;   // data members

  addToCart() {}             // member functions
  removeFromCart() {}
  displayProduct() {}
  buyProduct() {}
}
```

<!-- page 32 -->

> Side notes: In JS, classes are "fake" (it's just a wrapper). By default you get a constructor when creating a class.

## Constructor

- A JS class has a special function (method) called the **constructor**.
- What is so special about it? Whenever we create an object using classes, the constructor is the first method that is automatically called by JS.
- It is already available for any class you make. The default version of this constructor is called the **default constructor**.
- We can change the implementation of the default constructor.

```js
typeof Product; // "function"

class Product {
  constructor() { // `constructor` – reserved word?
    console.log("custom constructor");
  }
}
```

### How to create an object using this blueprint (class)?

- There is a keyword called `new` which can help us create an object out of a class.
- Do not map this `new` keyword in JS to other languages.

```js
let obj = new Product();
```

### Q. How does `new` work?

Every time we call `new`, it does the following 4-step procedure:

1. It creates a brand new, plain and absolutely empty object.
2. It calls the constructor of the class and passes the newly created object (not as a parameter) but inside a keyword called `this`. So the constructor automatically has access to the `this` keyword, and when we call `new`, this `this` keyword has access to the plain object created in step 1, and the constructor can now use the `this` keyword inside it. And then whatever logic is in the constructor is executed.
3. In step 3, `new` triggers everything that needs to be done for prototypes.
4. Now, if an object is manually returned from the constructor, then this manually returned object is stored in the calling variable. In any other case — i.e. either we don't return anything or we return something other than an object — the constructor doesn't care about it and

<!-- page 33 -->

returns the value inside the `this` keyword.

```js
constructor() {
  return { obj: 1 }; // anything of type object → the original object is replaced by { obj: 1 }
}
```

- Otherwise it will return `this` (the whole object) (and here you can return anything else — it is ignored).

### How to initialize the class variables (data members)

```js
constructor(name, age) {
  this.name = name; // updating / init the value from the params
  this.age = age;
}

let iphone = new Mobile("xyz", 23); // (very bad example)
```

- Or you can do → `obj.name = "..."; obj.age = 23;` etc.
- If the key does not exist, it is created — so you can define (init) a property without explicitly declaring the variable in the object.

## `this` Keyword in JS

- `this` in JS works very differently.
- `this` is a keyword available to be accessed in any function, or even outside any function, and in classes as well.
- If we can use the `this` keyword anywhere, then what's the value stored inside `this`?
- In most cases `this` refers to a **call site**. The call site can be an object, or a position, or may even be the `new` keyword. It refers to the entity which is calling the function that uses `this`.

```js
let obj = {
  a: 10,
  b: 20,
  fn: function () {
    console.log(this.a, this.b);
  },
};

obj.fn(); // 10 20 → here obj is calling (call site), and `this` refers to obj
```

<!-- page 34 -->

> Side note: [window object → global object]

```js
let obj = {
  x: 10,
  y: 20,
  z: {
    x: 99,
    fn: function () {
      console.log(this.x, this.y); // 99 undefined
    },
  },
};

obj.z.fn(); // call site is z
```

**Note:** There is an exception: the `this` keyword does **not** refer to the call site if it is used inside an arrow function.

- If `fn` above were an arrow function: `obj.z.fn()` → `undefined undefined`.
- In the case of an arrow function, `this` is resolved using **lexical scoping**.

```js
let obj = {
  x: 10,
  y: 20,
  fn: function () {
    const arrfx = () => {
      console.log(this.x, this.y); // 10 20
    };
    arrfx();
  },
};

obj.fn();
```

- Here `() => {}` is inside a normal function (this is a way to resolve `this` for an arrow function). It checks: does `this` exist in the arrow function? No → move to the parent scope. Does it exist there? Yes, because the normal function is the parent scope (this function has access to the `this` keyword).

Example:

```js
let obj = {
  x: 10,
  y: 20,
  fn: function () {
    x = 1; y = 2; // local variables (written without a declaration keyword in the notes)
    const arrow = () => {
      console.log(this.x, this.y); // 10 20 – `this` exists in the function fn (x = 10, y = 20)
    };
    console.log(x, y); // 1 2 – no `this`, local variables
    arrow();
  },
};

obj.fn();
```

<!-- page 35 -->

> Side notes: (You will get a browser compatibility error.) `constructor` is not a keyword? Why is that? → JS developers did this.

## Problem With the Current Class Implementation — Encapsulation

- In the current implementation, we do not add any security on updating the values of the data members in the class.
- After class creation, anyone can come up and update the object of our class without any issues. This violates a fundamental principle of OOP, called **encapsulation**.
- It says that classes are a bundle of implementation in themselves. In any case, we should not be required to modify the data members of a class from outside. Why? Because then our data members could be assigned any random value without any issue.
- To resolve this, we can hide our data members from being accessed outside the class. How? Make them **private**, i.e. the data members will be accessed for read & write only inside the class.
- To make a data member private, just prepend `#` before its declaration.

```js
#name; #price; #description; // private
```

- You are not able to access them directly outside the class:
  - `obj.#name` ✗ (error)
  - `obj.name` → it will create/reference a new, different variable.
- If you want to get & set the value, then write **getters & setters**. How? (with validation logic)

```js
// setter
setPrice(price) {
  if (price > 0) { this.#price = price; }
  else { console.log("Invalid price"); }
}

// getter
getPrice() { return this.#price; }
```

How to use:

```js
obj.setPrice(value);
obj.getPrice();
```

<!-- page 36 -->

> Side notes: In JS you can't create multiple constructors. [JS is an "object linked to an object" language.]

- You can't make a constructor private (compile error).
- If you want to do validation before object creation, then a constructor is required.
- A **design pattern** is nothing but a way to write code such that your code would be easy to maintain, debug, etc.

**Question:** If you have multiple data members, then how will you assign the values to those members? Either by passing all the values in the constructor (looks messy, must maintain order, etc.) or by creating getters/setters — but then we need to create more getters & setters.

- So the solution is to pass an object inside the constructor which contains the data. (It is also a type of pattern — a design pattern.)

### Alternative way to create getters & setters — using keywords

```js
get price() {}
set price(value) {}
```

- `get` / `set` are keywords. You have to use a different name (from the private field). Access → `obj.price` (no need to call it like a function).

## Class as a Wrapper on Function

How to create object behaviour using a function:

```js
function Animal(name, age) {
  this.name = name;
  this.age = age;
  this.displayAnimal = function () {
    console.log(this.name, this.age);
  };
  function fx() { console.log(this.name, this.age); }
}

let dog = new Animal("cherry", 2);

dog.name;           // ✓
dog.age;            // ✓
dog.displayAnimal(); // ✓
dog.fx();           // ✗ not visible, because it is not created using `this`
```

<!-- page 37 -->

> Side note: DNA → Deoxyribonucleic Acid :)

- In JS, every class we write is a wrapper over a function. In older versions the `class` keyword did not exist, hence to do the blueprinting we used to have only functions.
- The `Animal` function acts as a **function constructor** (do not use an arrow function for this).

## Static Variable

- Those variables which are only associated with the class (not with the object).

```js
class Product {
  static x = 10;
  constructor(name, price) {
    this.name = name;
    this.price = price;
  }
}

let p1 = new Product("watch", 1000);
p1.x;      // ✗ not accessible [not an error] → undefined
Product.x; // 10
```

- You can make it private (if you want).

## Builder Pattern in JS

```js
class Product {
  constructor(builder) {
    this.name = builder.name;
    this.price = builder.price;
  }

  static get Builder() {
    class Builder {
      constructor() {
        this.name = "";
        this.price = 0;
      }
      setName(incomingName) {
        this.name = incomingName;
        return this;
      }
      setPrice(incomingPrice) {
        this.price = incomingPrice;
        return this;
      }
      build() {
        return new Product(this);
      }
    }
    return Builder; // (class)
  }
}
```

How to create a Product object:

```js
const p1 = new Product.Builder()
  .setName("iPhone 16")
  .setPrice(120000)
  .build();
```

(In the notes the chain is written as `.name('iPhone16').price(120000)`; the methods are `setName` / `setPrice` as defined above.)

<!-- page 38 -->

> Side notes: [Gang of Four] – design patterns. Static use case?

- `Product.Builder` returns a class `Builder`; to make an object of it you have to use the `new` keyword.
  - `new Product.Builder()` → creates an empty Builder object. Now you can access its methods,
  - and using `.build()` we are able to create a new Product object.

## Object Features & Intro to Prototypes

**Issue with getters/setters:** we can't apply validation to the object before its creation. For any reason, if we want a scenario where, due to some validation not being fulfilled, we have to stop the creation of the object, it is not possible here.

**Disadvantages of the Builder pattern:** for a smaller number of parameters this builder is not required, etc.

## Object Destructuring

- A mechanism using which we try to unpack an object into multiple variables.

```js
const obj = { a: 1, b: 2, c: 3 };

// destructuring
const { a, b, c } = obj;
console.log(a); // 1 – now you can use it directly
```

- If some variable does not exist (as a key), then it will store `undefined`.
- Destructuring an object into another object — another way:

```js
const obj2 = { ...obj1 /* , ... */ }; // spread operator
```

- If some key already exists in the new object and it also exists in `...obj`, then this will update the new key/value.

<!-- page 39 -->

### Alias

You can use another name for an existing key (in an object):

```js
const product = { updatedName: "ritesh" };
const { updatedName: name } = product; // alias
```

- Now you can use `name` as the variable, but you can't use `updatedName`.

### Nested objects

If you have a nested object in an object (e.g. a `category` object) and you want the `categoryId` key from it:

```js
const product = { /* ..., */ category: { categoryId: 1 } };

const { category: { categoryId } } = product;
// or
const { categoryId } = product.category;
```

### Tips & tricks for object destructuring

```js
const obj = { ...obj1, ...obj2, ...obj3 }; // merge
const clone = { ...obj };                  // clone an object

// create a new object with an updated value
const newObj = { ...obj, updatedVal: value }; // key already exists → here updating
```

- Default value (if it does not exist, then take this):

```js
const { name, discount = 10 } = product;
```

## Rest Parameter

- `{ ... }` — the rest operator is the opposite of the spread operator.
- If you want to remove one or more keys from an object:

```js
const { price, ...restObj } = product; // restObj does not have the price key
```

- `fx(...args)` — when you don't know how many (indefinite) args/params are required.

<!-- page 40 -->

> Side note: H.W → Tic-Tac-Toe game

### Spread / rest operator with arrays

```js
const arr = [20, function fx() {}];
const [val, setVal] = arr; // your defined variables – only the sequence matters

const [first, ...rest] = arr; // destructuring (rest)

const newArr = [20, 30, ...arr]; // spread
```

(The notes write `const [arr, ...arr]`; renamed here so it is valid JS.)

## Prototype in JS

- A lot of times you will find people saying JS is not OO; instead it is an "object linked to an object" kind of language. The sole reason for this is **prototype**.
- **What is a prototype?** It is the mechanism by which objects share properties with other objects.
- What happens inside JS while running your code? (This is also a part of execution.)

Diagram (described):

- **Internal setup in JS:** a function named `Object` has a `.prototype` property pointing to an object (an unnamed entity, an object without a name) containing `toString()`, `isPrototypeOf()`, `valueOf()` and `constructor`. The `constructor` (is a part of it) points back to the `Object` function.
- **Our code setup:** for `Product` (a function), JS creates `Product.prototype` → an unnamed entity (object) holding all methods of `Product` + `constructor`. JS links it (hidden relation) to `Object.prototype`.
- `p = new Product()` → a plain object; the hidden linking to `Product.prototype` happens in the 3rd step of `new`.

<!-- page 41 -->

> Side note: [Classes are nothing but functions in JS]

- `Object.prototype.constructor` → returns the `Object` function.
- All functions (methods) that you define inside a class also exist in the prototype object:
  - `Product.prototype` → gets all methods; has `constructor`.
  - `Product.prototype.constructor` points to the `Product` class (function).
- Also, JS links your `Product.prototype` with `Object.prototype`.

```js
const p = new Product();
p.method();
```

- This method is not defined in the constructor, but we are still able to access it, because JS searches the unnamed entity above (`Product.prototype`) — if it is present there, call it; otherwise search above → `Object.prototype` — and then finally you get it.
- This is nothing but **prototyping**.

But:

```js
class Product {
  constructor() {
    this.display = () => {};
  }
  display() {}
}

const p = new Product();
p.display(); // this will call the function initialized in the constructor
```

<!-- page 42 -->

> Side notes (book recommendations): [dunder proto] [Robert Lafore → C++ OOP] [Galvin → OS] [You Don't Know JS → all parts — BEST BOOK] [Cormen → Algorithms]

### How to access the hidden link

```js
const obj = new Product();
obj.__proto__;             // "dunder proto" – it will return all methods
obj.__proto__.methodName(); // you are able to call the method this way
```

### But if you are defining the constructor using a function

```js
function Product(name) {
  this.name = name;
  this.fx = function () { console.log(this); };
}
```

- Now this `fx` exists in the object (not in the prototype object).

### How to add a new method inside your prototype

```js
Product.prototype.display = function () {}; // unnamed
```

### Q. What is the advantage of prototypes in JS?

- E.g. BookMyShow has several features — (i) movie ticket booking, (ii) comedy show ticket booking, etc.
- Internally both use the same logic for booking tickets. So instead of writing it on both sides, we can write it once and use (extend) this property.
- Diagram: an `Event` class with `ticketBooking()`; `Movie` and `ComedyShow` inherit the property from `Event`.

<!-- page 43 -->

## Inheritance (`extends`)

How to achieve it in code:

```js
class Event {
  ticketBooking() {}
}

class Movie extends Event {
  // Now here you can use this ticketBooking() after creating an object
}
```

At the prototype level (diagram):

- `Object` function ⇄ (`prototype` / `constructor`) ⇄ `Object.prototype`
- `Event` function ⇄ (`prototype` / `constructor`) ⇄ `Event.prototype` (has `ticketBooking()`), which links up to `Object.prototype`
- `Movie` function ⇄ (`prototype` / `constructor`) ⇄ `Movie.prototype`, and `Movie.prototype.__proto__` → `Event.prototype`

## Call, Apply and Bind Functions in JS

- These are very useful functions in JS that can help us manipulate the value pointed to by the `this` keyword.
- **`call()`** — a function in JS that helps you control and change the value of the `this` keyword inside a function. When we execute the function, what the `this` keyword should point to can be manipulated using the `call` function of JS.

<!-- page 44 -->

```js
const obj = {
  name: "ritesh",
  greet: function () {
    console.log("name is", this.name);
  },
};

const newObj = { name: "sonu" };

obj.greet.call(newObj); // sonu
```

- Now I am calling `greet` from `newObj`, manipulating the `this` value (`this` pointing to `newObj`).

**Note:** But you can't do this with an arrow function — with `call()` too, an arrow function's `this` is resolved lexically.

If your function is taking parameters, then? — they are given comma-separated:

```js
obj.fx.call(newObj, arg1, arg2);
```

### 2. `apply()`

- It works exactly like the `call` function. The only difference is, instead of taking `n` number of args, it takes only two args:
  1. args1 → the object to which `this` will point.
  2. An array of values which will be passed to the function.

```js
obj.greet.apply(newObj, ["abc", "cde"]); // you can pass it as rest operator
```

### Interesting case

```js
var name = "abcd"; // var / let
let obj = {
  name: "xyz",
  greet: () => { console.log(this.name); },
};

obj.greet.call(); // (nothing passed, so by default → global scope)
```

- Output → it will print `abcd` in the browser; it will print `undefined` in Node.js.

<!-- page 45 -->

### 3. `bind()`

- The bind function works exactly like `call`, but instead of immediately invoking the function, it returns a new function which has the `this` keyword bound to the object passed as argument. And now this new function can be called anywhere.

```js
const f = obj.greet.bind(newObj);
f(params); // params – not in an array
```

**Note:** Then how to use an arrow function?

1. You can wrap it inside a normal function.
2. You can wrap it, but create a variable →

```js
greet: function () {
  const self = this; // points to this (obj1)
  const fn = () => { console.log(self.name); };
}
```

**Note:** How to implement inheritance without classes?

- Then you can use [`call`, `apply`, `bind`], using dunder proto → in function objects.
- Diagram: `Events` function ⇄ `Events.prototype`; `Movie` ⇄ `Movie.prototype`. We want `Movie.prototype` to link to `Events.prototype` (which links to `Object.prototype`), and we don't want `Movie.prototype` to link directly to `Object.prototype`.

```js
Movie.prototype.__proto__ = Events.prototype; // connection established

const m = new Movie();
m.eventsFn(); // now we can call the Events method
```

<!-- page 46 -->

**Note:** JS gives you a new mechanism to do the same thing:

```js
function Event(dateOfEvent) {
  this.dateOfEvent = dateOfEvent;
}
Event.prototype.bookEvent = function () { console.log("booking event"); };

function Movie(name) {
  this.name = name;
}

// connection
Movie.prototype = Object.create(Event.prototype);

const m = new Movie("deadpool");
m.bookEvent(); // yes, now you can access it
```

### Note: What is the `super` function?

```js
class Events {
  constructor(dateOfEvent) { this.dateOfEvent = dateOfEvent; }
  bookEvent() { console.log("booked event"); }
}

class Movie extends Events {
  constructor(name, movieDate) {
    super(movieDate); // it is mandatory to call this to initialize the Events (class) members
    this.movieName = name;
  }
}

const dp = new Movie("deadpool", "2025-06-10");
```

**Without objects (classes)** — how to pass the parent's data:

```js
function Events(eventDate) { this.eventDate = eventDate; }

function Movie(movieName, movieDate) {
  Events.call(this, movieDate);
  this.movieName = movieName;
}

const newMovie = new Movie("DP", "2023-04-23");
```

<!-- page 47 -->

> Side note: Type conversion → Implicit (by default) (coercion); Explicit (if you want to manually convert).

## Lecture — Type Coercion (very important)

- What is an abstract operation? — (left blank in the notes)

### (1) Abstract operation — `ToBoolean(args)`

- Conversion of any data type into a boolean (`true` / `false`).
- **Falsy values:** `undefined`, `null`, `NaN`, `+0`, `-0`, `false`, `""` → always return `false`. (`+0` or `0` — both are the same.)
- **Truthy values:** all the rest (except falsy) convert to `true`.
- But — [the rest continues in the green-colour copy (the next notebook)].
