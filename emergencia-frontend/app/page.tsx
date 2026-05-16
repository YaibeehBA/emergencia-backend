import AppHeader from '@/components/app-header'
import HomeContent from '@/components/home-content'
import AppFooter from '@/components/app-footer'

export default function HomePage() {
  return (
    <>
      <AppHeader />
      <main className="pt-16 sm:pt-20 min-h-screen">
        <HomeContent />
        <div className="max-w-3xl mx-auto">
          <AppFooter narrow />
        </div>
      </main>
    </>
  )
}
