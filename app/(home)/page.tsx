import Link from 'next/link';

const sections = [
  {
    title: '1. Python, in depth',
    description:
      'Object model → data structures → functions & closures → OOP & the data model → generators → async & the GIL → typing → CPython internals, plus interview Q&A and output-based practice.',
    href: '/docs/python',
  },
  {
    title: '2. FastAPI',
    description:
      'ASGI, validation, dependency injection, databases, auth, testing and deployment, then FastAPI for AI engineering: LLM calls, streaming, structured outputs, RAG, agents and model serving.',
    href: '/docs/fastapi',
  },
  {
    title: '3. Backend From First Principles',
    description:
      'HTTP, routing, auth, REST, Postgres, caching, queues, security, scaling, object storage, real-time, testing and DevOps, with diagrams.',
    href: '/docs/backend-first-principles',
  },
  {
    title: '4. GenAI Full Stack Handbook',
    description:
      '30 chapters on production GenAI: LLM internals, embeddings, RAG, agents, inference, GPUs, MLOps, security, system design and interviews.',
    href: '/docs/genai-handbook',
  },
];

export default function HomePage() {
  return (
    <div className="flex flex-col justify-center items-center text-center flex-1 px-4 py-16">
      <h1 className="text-3xl font-bold mb-3">Python &amp; Backend Learning</h1>
      <p className="text-fd-muted-foreground mb-10 max-w-xl">
        A study hub for Python from first principles, FastAPI, backend engineering and GenAI.
      </p>
      <div className="grid gap-4 sm:grid-cols-2 w-full max-w-3xl text-left">
        {sections.map((s) => (
          <Link
            key={s.href}
            href={s.href}
            className="rounded-xl border bg-fd-card p-6 transition-colors hover:bg-fd-accent"
          >
            <h2 className="font-semibold mb-2">{s.title}</h2>
            <p className="text-sm text-fd-muted-foreground">{s.description}</p>
          </Link>
        ))}
      </div>
    </div>
  );
}
