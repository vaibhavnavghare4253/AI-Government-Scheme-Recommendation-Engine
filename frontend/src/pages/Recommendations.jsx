export default function Recommendations() {
  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-12">
      <div className="mb-8">
        <h1 className="text-3xl font-bold text-gray-900">Your Recommendations</h1>
        <p className="mt-2 text-gray-600">
          Personalized scheme recommendations based on your profile
        </p>
      </div>

      <div className="bg-blue-50 border border-blue-200 rounded-lg p-6 text-center">
        <svg className="mx-auto h-12 w-12 text-blue-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
        </svg>
        <h3 className="mt-4 text-lg font-medium text-gray-900">Complete Your Profile</h3>
        <p className="mt-2 text-sm text-gray-600">
          To get personalized recommendations, please complete your profile first.
        </p>
        <div className="mt-6">
          <a
            href="/profile"
            className="inline-flex items-center px-4 py-2 border border-transparent text-sm font-medium rounded-md shadow-sm text-white bg-blue-600 hover:bg-blue-700"
          >
            Go to Profile
          </a>
        </div>
      </div>

      {/* Sample Recommendation Card (for demo) */}
      <div className="mt-8 bg-white rounded-lg shadow-md p-6 opacity-50">
        <div className="flex items-start justify-between">
          <div className="flex-1">
            <div className="flex items-center">
              <span className="inline-flex items-center px-3 py-0.5 rounded-full text-sm font-medium bg-green-100 text-green-800">
                95% Match
              </span>
              <span className="ml-2 inline-flex items-center px-2 py-0.5 rounded text-xs font-medium bg-blue-100 text-blue-800">
                Agriculture
              </span>
            </div>
            <h3 className="mt-4 text-xl font-semibold text-gray-900">
              PM-KISAN (Sample)
            </h3>
            <p className="mt-2 text-gray-600">
              You are eligible for this scheme because you are a farmer with land ownership less than 2 hectares.
            </p>
            <div className="mt-4">
              <p className="text-2xl font-bold text-green-600">₹6,000/year</p>
              <p className="text-sm text-gray-500">Direct Cash Transfer</p>
            </div>
            <div className="mt-4">
              <h4 className="text-sm font-medium text-gray-900">Required Documents:</h4>
              <ul className="mt-2 list-disc list-inside text-sm text-gray-600">
                <li>Aadhaar Card</li>
                <li>Land Records</li>
                <li>Bank Account Details</li>
              </ul>
            </div>
          </div>
        </div>
        <div className="mt-6 flex space-x-3">
          <button className="flex-1 px-4 py-2 bg-blue-600 text-white text-sm font-medium rounded-md hover:bg-blue-700">
            Apply Now
          </button>
          <button className="px-4 py-2 border border-gray-300 text-gray-700 text-sm font-medium rounded-md hover:bg-gray-50">
            Learn More
          </button>
        </div>
      </div>
    </div>
  )
}
