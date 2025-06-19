import { ReactNode } from 'react'

interface DashboardLayoutProps {
  children: ReactNode
}

export default function DashboardLayout({ children }: DashboardLayoutProps) {
  return (
    <div className="min-h-screen bg-background">
      {/* Navigation Header */}
      <header className="border-b bg-white">
        <div className="container mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex h-16 items-center justify-between">
            <div className="flex items-center">
              <h1 className="text-xl font-semibold text-gray-900">AI UI Generator</h1>
            </div>
            
            <nav className="hidden md:flex space-x-8">
              <a href="/home" className="text-gray-600 hover:text-gray-900">
                Dashboard
              </a>
              <a href="/projects" className="text-gray-600 hover:text-gray-900">
                Projects
              </a>
              <a href="/generate" className="text-gray-600 hover:text-gray-900">
                Generate
              </a>
              <a href="/settings" className="text-gray-600 hover:text-gray-900">
                Settings
              </a>
            </nav>

            <div className="flex items-center space-x-4">
              {/* TODO: Add user menu */}
              <button className="bg-primary text-primary-foreground px-4 py-2 rounded-md hover:bg-primary/90">
                Sign Out
              </button>
            </div>
          </div>
        </div>
      </header>

      {/* Main Content */}
      <main className="flex-1">
        {children}
      </main>
    </div>
  )
}
