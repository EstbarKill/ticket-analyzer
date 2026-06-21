"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";

const LINKS = [
  { href: "/", label: "Dashboard", glyph: "01" },
  { href: "/tickets", label: "Tickets", glyph: "02" },
  { href: "/assistant", label: "Asistente IA", glyph: "03" },
];

export default function Sidebar() {
  const pathname = usePathname();

  return (
    <aside className="flex h-screen w-56 flex-col justify-between border-r border-line bg-surface px-5 py-6">
      <div>
        <div className="mb-8">
          <p className="font-mono text-xs uppercase tracking-widest text-muted">
            Soporte · IA
          </p>
          <h1 className="mt-1 text-lg font-semibold leading-tight text-ink">
            Ticket Analyzer
          </h1>
        </div>
        <nav className="flex flex-col gap-1">
          {LINKS.map((link) => {
            const active = pathname === link.href;
            return (
              <Link
                key={link.href}
                href={link.href}
                className={`flex items-center gap-3 rounded-md px-3 py-2 text-sm transition-colors ${
                  active
                    ? "bg-accent-soft text-accent font-medium"
                    : "text-ink/80 hover:bg-canvas"
                }`}
              >
                <span className="font-mono text-xs text-muted">{link.glyph}</span>
                {link.label}
              </Link>
            );
          })}
        </nav>
      </div>
      <p className="font-mono text-[11px] leading-relaxed text-muted">
        Datos procesados localmente. El proveedor de IA se controla por
        variables de entorno.
      </p>
    </aside>
  );
}
