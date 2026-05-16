import type { Metadata } from 'next'
import { Roboto } from 'next/font/google'
import { Toaster } from 'sonner'
import './globals.css'

const roboto = Roboto({
  subsets: ['latin'],
  weight: ['300', '400', '500', '700'],
  variable: '--font-roboto',
})

export const metadata: Metadata = {
  title: 'SENTRIA — Sistema Inteligente de Validación Hospitalaria',
  description:
    'Validación instantánea de cobertura en emergencias. Hospital y aseguradora sincronizados con agente IA.',
}

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode
}>) {
  return (
    <html lang="es-EC" className={`dark ${roboto.variable}`}>
      <body className="min-h-screen bg-black font-sans antialiased">
        {children}
        <Toaster
          theme="dark"
          toastOptions={{
            style: {
              background: '#202020',
              border: '1px solid #333',
              color: '#ffffff',
              borderRadius: '0',
            },
          }}
        />
      </body>
    </html>
  )
}
