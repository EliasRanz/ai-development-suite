'use client'

import { useState } from 'react'

interface ChatInterfaceProps {
  onPromptSubmit: (prompt: string) => void
  isGenerating: boolean
}

export default function ChatInterface({ onPromptSubmit, isGenerating }: ChatInterfaceProps) {
  const [prompt, setPrompt] = useState('')

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault()
    if (prompt.trim() && !isGenerating) {
      onPromptSubmit(prompt)
      setPrompt('')
    }
  }

  return (
    <div className="flex flex-col h-full">
      {/* Chat History - TODO: Implement */}
      <div className="flex-1 overflow-y-auto p-4 space-y-4">
        <div className="text-center text-muted-foreground">
          Start a conversation to generate UI components
        </div>
        {/* TODO: Add chat message components */}
      </div>
      
      {/* Input Form */}
      <form onSubmit={handleSubmit} className="p-4 border-t">
        <div className="flex space-x-2">
          <input
            type="text"
            value={prompt}
            onChange={(e) => setPrompt(e.target.value)}
            placeholder="Describe the UI component you want to create..."
            className="flex-1 px-3 py-2 border rounded-md focus:outline-none focus:ring-2 focus:ring-primary"
            disabled={isGenerating}
          />
          <button
            type="submit"
            disabled={!prompt.trim() || isGenerating}
            className="px-4 py-2 bg-primary text-primary-foreground rounded-md hover:bg-primary/90 disabled:opacity-50 disabled:cursor-not-allowed"
          >
            {isGenerating ? 'Generating...' : 'Generate'}
          </button>
        </div>
      </form>
    </div>
  )
}
