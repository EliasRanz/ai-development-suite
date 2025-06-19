'use client'

import ChatInterface from '@/components/ChatInterface'
import PreviewPane from '@/components/PreviewPane'
import { useState } from 'react'
import { generateAI, createAIStreamClient } from '@/lib/sse'

export default function DashboardLayout({
  children,
}: {
  children: React.ReactNode
}) {
  const [generatedCode, setGeneratedCode] = useState('')
  const [isGenerating, setIsGenerating] = useState(false)

  const handlePromptSubmit = async (prompt: string) => {
    setIsGenerating(true)
    setGeneratedCode('')
    
    try {
      // Start AI generation
      const { sessionId } = await generateAI(prompt)
      
      // Setup streaming client
      const streamClient = createAIStreamClient(sessionId, {
        onMessage: (data) => {
          setGeneratedCode(prev => prev + data)
        },
        onError: (error) => {
          console.error('Streaming error:', error)
          setIsGenerating(false)
        },
        onClose: () => {
          setIsGenerating(false)
        }
      })
      
      streamClient.connect()
      
    } catch (error) {
      console.error('Generation error:', error)
      setIsGenerating(false)
    }
  }

  return (
    <div className="h-screen flex flex-col">
      {/* Header */}
      <header className="border-b p-4">
        <div className="flex items-center justify-between">
          <h1 className="text-xl font-semibold">AI UI Generator</h1>
          <div className="flex items-center space-x-4">
            {/* TODO: Add user menu, settings, etc. */}
            <button className="px-3 py-1 text-sm border rounded hover:bg-gray-50">
              Settings
            </button>
            <button className="px-3 py-1 text-sm border rounded hover:bg-gray-50">
              Sign Out
            </button>
          </div>
        </div>
      </header>
      
      {/* Main Content */}
      <div className="flex-1 flex overflow-hidden">
        {/* Chat Interface */}
        <div className="w-1/2 border-r">
          <ChatInterface 
            onPromptSubmit={handlePromptSubmit}
            isGenerating={isGenerating}
          />
        </div>
        
        {/* Preview Pane */}
        <div className="w-1/2">
          <PreviewPane 
            generatedCode={generatedCode}
            isLoading={isGenerating}
          />
        </div>
      </div>
    </div>
  )
}
