import api from './index'

export function fetchDocuments() {
  return api.get('/documents')
}

export function uploadDocument(file: File) {
  const formData = new FormData()
  formData.append('file', file)
  return api.post('/documents', formData, {
    headers: { 'Content-Type': 'multipart/form-data' },
  })
}

export function deleteDocument(fileId: string) {
  return api.delete(`/documents/${fileId}`)
}
