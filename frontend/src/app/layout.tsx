import type { Metadata } from 'next';
import './globals.css';

export const metadata: Metadata = {
  title: '10-Avatar Character Identity Studio | India-Centric AI Video',
  description: 'Persistent character identity pipeline inspired by Higgsfield Soul ID, powered by Wan 2.2 / Fal.ai architecture.',
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en">
      <body>
        <div className="app-container">
          <header className="app-header">
            <div className="brand-wrapper">
              <div className="brand-icon">🇮🇳</div>
              <div>
                <h1 className="brand-title">Character Identity Studio</h1>
                <p className="brand-subtitle">Persistent Indian Character Registry • Wan 2.2</p>
              </div>
            </div>

            <div className="header-badges">
              <span className="pill-badge engine">Wan 2.2 A14B</span>
              <span className="pill-badge inspiration">Higgsfield Soul ID Paradigm</span>
            </div>
          </header>

          <main style={{ flex: 1 }}>
            {children}
          </main>
        </div>
      </body>
    </html>
  );
}
