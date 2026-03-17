import type { Metadata } from 'next';
import './globals.css';

export const metadata: Metadata = {
  title: 'Auto Peças — Painel de Anúncios',
  description: 'Pipeline de publicação de peças usadas no Mercado Livre',
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="pt-BR">
      <body className="min-h-screen bg-gray-50 text-gray-900 antialiased">
        <header className="sticky top-0 z-10 border-b border-gray-200 bg-white px-4 py-3">
          <div className="mx-auto flex max-w-3xl items-center justify-between">
            <span className="font-semibold text-gray-900">Auto Peças Dashboard</span>
          </div>
        </header>
        <main className="mx-auto max-w-3xl px-4 py-6">{children}</main>
      </body>
    </html>
  );
}
