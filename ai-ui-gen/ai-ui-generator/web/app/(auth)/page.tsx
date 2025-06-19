'use client'

import { signIn, getSession } from 'next-auth/react'
import { useEffect, useState } from 'react'

export default function AuthPage() {
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    const checkSession = async () => {
      const session = await getSession()
      if (session) {
        // Redirect to dashboard if already authenticated
        window.location.href = '/dashboard'
      }
      setLoading(false)
    }
    
    checkSession()
  }, [])

  const handleGoogleSignIn = async () => {
    try {
      await signIn('google', { 
        callbackUrl: '/dashboard',
        redirect: true 
      })
    } catch (error) {
      console.error('Sign in error:', error)
    }
  }

  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary mx-auto"></div>
          <p className="mt-4 text-muted-foreground">Loading...</p>
        </div>
      </div>
    )
  }

  return (
    <div className="min-h-screen flex items-center justify-center bg-background">
      <div className="w-full max-w-md space-y-8">
        <div className="text-center">
          <h1 className="text-3xl font-bold">AI UI Generator</h1>
          <p className="mt-2 text-muted-foreground">
            Sign in to start generating beautiful UI components
          </p>
        </div>
        
        <div className="space-y-4">
          <button
            onClick={handleGoogleSignIn}
            className="w-full flex items-center justify-center px-4 py-2 border border-gray-300 rounded-md shadow-sm text-sm font-medium text-gray-700 bg-white hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-primary"
          >
            {/* TODO: Add Google icon */}
            <span className="ml-2">Continue with Google</span>
          </button>
          
          {/* TODO: Add other auth providers if needed */}
        </div>
        
        <div className="text-center text-sm text-muted-foreground">
          By signing in, you agree to our Terms of Service and Privacy Policy
        </div>
      </div>
    </div>
  )
}
