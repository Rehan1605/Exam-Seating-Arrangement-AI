const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:5000'

export async function uploadCsv(file) {
  const formData = new FormData()
  formData.append('file', file)

  const response = await safeFetch(`${API_BASE_URL}/upload`, {
    method: 'POST',
    body: formData,
  })

  return parseResponse(response)
}

export async function saveHalls(halls) {
  const response = await safeFetch(`${API_BASE_URL}/save-halls`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ halls }),
  })

  return parseResponse(response)
}

export async function generateSeating(payload) {
  const response = await safeFetch(`${API_BASE_URL}/generate-seating`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(payload),
  })

  return parseResponse(response)
}

export async function regenerateSeating(payload) {
  const response = await safeFetch(`${API_BASE_URL}/regenerate`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(payload),
  })

  return parseResponse(response)
}

export async function generatePdf(payload = {}) {
  const response = await safeFetch(`${API_BASE_URL}/generate-pdf`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(payload),
  })

  return parseResponse(response)
}

export function getPdfDownloadUrl() {
  return `${API_BASE_URL}/download-pdf`
}

export async function downloadPdf() {
  const response = await safeFetch(getPdfDownloadUrl())
  if (!response.ok) {
    const data = await response.json()
    throw new Error(data.error || 'Unable to download PDF')
  }

  return response.blob()
}

async function safeFetch(url, options) {
  try {
    return await fetch(url, options)
  } catch {
    throw new Error(`Cannot reach backend at ${API_BASE_URL}. Start the Flask server, then try again.`)
  }
}

async function parseResponse(response) {
  const data = await response.json().catch(() => ({}))
  if (!response.ok) {
    throw new Error(data.error || 'Request failed')
  }
  return data
}
