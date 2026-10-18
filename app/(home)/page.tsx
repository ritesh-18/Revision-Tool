import Link from 'next/link';

const sections = [
  {
    title: '1. JS & TS Notes',
    description:
      'Start here: basics → functions & scope → coercion → objects & OOP → async, plus 350 practice questions.',
    href: '/docs/js-ts',
  },
  {
    title: '2. LLD in TypeScript',
    description:
      'TypeScript essentials, SOLID, design patterns, concurrency, and 30+ machine-coding case studies up to SDE-2.',
    href: '/docs/lld',
  },
];

export default function HomePage() {
  return (
    <div className="flex flex-col justify-center items-center text-center flex-1 px-4 py-16">
      <h1 className="text-3xl font-bold mb-3">LLD &amp; JS Learning</h1>
      <p className="text-fd-muted-foreground mb-10 max-w-xl">
        A study hub for Low-Level Design and machine-coding interviews, written in TypeScript.
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
