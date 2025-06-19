export default function GeneratePage() {
  return (
    <div className="h-full flex">
      {/* Chat Interface */}
      <div className="w-1/2 border-r">
        <div className="p-6">
          <h2 className="text-xl font-semibold text-gray-900 mb-4">AI Chat</h2>
          <div className="bg-gray-100 rounded-lg p-4 h-96 mb-4">
            <p className="text-gray-500">Chat interface will be implemented here...</p>
          </div>
          <div className="flex space-x-2">
            <input
              type="text"
              placeholder="Describe the UI component you want to create..."
              className="flex-1 px-3 py-2 border rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
            />
            <button className="bg-blue-600 text-white px-4 py-2 rounded-md hover:bg-blue-700">
              Generate
            </button>
          </div>
        </div>
      </div>

      {/* Preview Pane */}
      <div className="w-1/2">
        <div className="p-6">
          <h2 className="text-xl font-semibold text-gray-900 mb-4">Preview</h2>
          <div className="bg-gray-100 rounded-lg p-4 h-96">
            <p className="text-gray-500">Generated component preview will appear here...</p>
          </div>
          <div className="mt-4 flex space-x-2">
            <button className="px-4 py-2 border rounded-md hover:bg-gray-50">
              Copy Code
            </button>
            <button className="px-4 py-2 border rounded-md hover:bg-gray-50">
              Export
            </button>
          </div>
        </div>
      </div>
    </div>
  )
}
