export default function GlobalDashboard() {
  return (
    <div className="max-w-7xl mx-auto">
      <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
        <h2 className="text-xl font-semibold text-gray-900 mb-4">Dashboard</h2>
        <p className="text-gray-600">
          Global dashboard view showing metrics across all projects.
        </p>
        {/* TODO: Implement global dashboard with project metrics, charts, etc. */}
        <div className="mt-6 p-4 bg-blue-50 rounded-lg">
          <p className="text-blue-800 text-sm">
            📊 This will show analytics and metrics across all your projects.
          </p>
        </div>
      </div>
    </div>
  );
}
