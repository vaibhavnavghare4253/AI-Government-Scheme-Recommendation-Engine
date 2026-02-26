import { useState, useEffect } from 'react'
import axios from 'axios'

export default function Schemes() {
  const [schemes, setSchemes] = useState([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(null)

  useEffect(() => {
    fetchSchemes()
  }, [])

  const fetchSchemes = async () => {
    try {
      const response = await axios.get('http://localhost:8000/api/v1/schemes')
      setSchemes(response.data.schemes || [])
      setLoading(false)
    } catch (err) {
      setError('Failed to load schemes. Make sure the backend is running.')
      setLoading(false)
    }
  }

  if (loading) {
    return (
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-12">
        <div className="text-center">
          <div className="inline-block animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600"></div>
          <p className="mt-4 text-gray-600">Loading schemes...</p>
        </div>
      </div>
    )
  }

  if (error) {
    return (
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-12">
        <div className="bg-red-50 border border-red-200 rounded-lg p-4">
          <p className="text-red-800">{error}</p>
          <p className="text-sm text-red-600 mt-2">
            Run: <code className="bg-red-100 px-2 py-1 rounded">cd backend && uvicorn app.main:app --reload</code>
          </p>
        </div>
      </div>
    )
  }

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-12">
      <div className="mb-8">
        <h1 className="text-3xl font-bold text-gray-900">Government Schemes</h1>
        <p className="mt-2 text-gray-600">Browse all available government schemes</p>
      </div>

      {schemes.length === 0 ? (
        <div className="bg-yellow-50 border border-yellow-200 rounded-lg p-6 text-center">
          <p className="text-yellow-800">No schemes found. Run the seed script to add sample data:</p>
          <code className="block mt-2 bg-yellow-100 px-4 py-2 rounded">python scripts/seed-data.py</code>
        </div>
      ) : (
        <div className="grid grid-cols-1 gap-6 sm:grid-cols-2 lg:grid-cols-3">
          {schemes.map((scheme) => (
            <div key={scheme.id} className="bg-white rounded-lg shadow-md overflow-hidden hover:shadow-lg transition-shadow">
              <div className="p-6">
                <div className="flex items-center justify-between mb-4">
                  <span className="inline-flex items-center px-3 py-0.5 rounded-full text-sm font-medium bg-blue-100 text-blue-800">
                    {scheme.category}
                  </span>
                  {scheme.is_central && (
                    <span className="inline-flex items-center px-2 py-0.5 rounded text-xs font-medium bg-green-100 text-green-800">
                      Central
                    </span>
                  )}
                </div>
                <h3 className="text-lg font-semibold text-gray-900 mb-2">
                  {scheme.name}
                </h3>
                <p className="text-sm text-gray-600 mb-4 line-clamp-3">
                  {scheme.description}
                </p>
                <div className="flex items-center justify-between">
                  <div>
                    {scheme.benefit_amount && (
                      <p className="text-lg font-bold text-green-600">
                        ₹{scheme.benefit_amount.toLocaleString()}
                      </p>
                    )}
                    <p className="text-xs text-gray-500">{scheme.benefit_type}</p>
                  </div>
                  <button className="px-4 py-2 bg-blue-600 text-white text-sm font-medium rounded-md hover:bg-blue-700">
                    View Details
                  </button>
                </div>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  )
}
