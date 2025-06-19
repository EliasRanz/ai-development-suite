'use client'

interface PreviewPaneProps {
  generatedCode: string
  isLoading: boolean
}

export default function PreviewPane({ generatedCode, isLoading }: PreviewPaneProps) {
  return (
    <div className="flex flex-col h-full">
      {/* Preview Header */}
      <div className="flex items-center justify-between p-4 border-b">
        <h2 className="text-lg font-semibold">Preview</h2>
        <div className="flex space-x-2">
          {/* TODO: Add copy, export, and other action buttons */}
          <button className="px-3 py-1 text-sm border rounded hover:bg-gray-50">
            Copy Code
          </button>
          <button className="px-3 py-1 text-sm border rounded hover:bg-gray-50">
            Export
          </button>
        </div>
      </div>
      
      {/* Preview Content */}
      <div className="flex-1 flex">
        {/* Code View */}
        <div className="w-1/2 border-r">
          <div className="p-2 bg-gray-50 border-b">
            <span className="text-sm font-medium">Generated Code</span>
          </div>
          <div className="p-4 h-full overflow-auto">
            {isLoading ? (
              <div className="text-center text-muted-foreground">
                Generating code...
              </div>
            ) : generatedCode ? (
              <pre className="text-sm">
                <code>{generatedCode}</code>
              </pre>
            ) : (
              <div className="text-center text-muted-foreground">
                No code generated yet
              </div>
            )}
          </div>
        </div>
        
        {/* Live Preview */}
        <div className="w-1/2">
          <div className="p-2 bg-gray-50 border-b">
            <span className="text-sm font-medium">Live Preview</span>
          </div>
          <div className="p-4 h-full">
            {isLoading ? (
              <div className="text-center text-muted-foreground">
                Loading preview...
              </div>
            ) : generatedCode ? (
              <div className="border-2 border-dashed border-gray-200 rounded-lg p-4 h-full">
                {/* TODO: Implement safe code execution/preview */}
                <div className="text-center text-muted-foreground">
                  Preview will render here
                </div>
              </div>
            ) : (
              <div className="text-center text-muted-foreground">
                No preview available
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  )
}
