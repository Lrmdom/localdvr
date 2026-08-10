import { useState, useEffect } from 'react'
import { CameraSelector } from './components/CameraSelector'
import { VideoPlayer } from './components/VideoPlayer'
import { Timeline } from './components/Timeline'
import { getDetectionColor } from './utils/colors'

function App() {
  const [cameras, setCameras] = useState<string[]>([])
  const [selectedCamera, setSelectedCamera] = useState<string>('')
  const [videos, setVideos] = useState<any[]>([])
  const [selectedVideoUrl, setSelectedVideoUrl] = useState<string | null>(null)

  useEffect(() => {
    fetch('/api/cameras')
      .then(res => res.json())
      .then(data => setCameras(data))
  }, [])

  useEffect(() => {
    if (selectedCamera) {
      const today = new Date().toISOString().split('T')[0]
      fetch(`/api/videos?camera=${selectedCamera}&date=${today}`)
        .then(res => res.json())
        .then(data => setVideos(data))
    }
  }, [selectedCamera])

  return (
    <div style={{ display: 'grid', gridTemplateColumns: '250px 1fr', height: '100vh', gap: '1rem' }}>
      <CameraSelector cameras={cameras} onSelect={setSelectedCamera} />
      <main style={{ padding: '1rem', overflowY: 'auto' }}>
        <h1 style={{ margin: '0 0 1rem 0' }}>LocalDVR Viewer</h1>
        {selectedCamera && (
          <div style={{ display: 'flex', flexDirection: 'column', gap: '1rem' }}>
            <VideoPlayer url={selectedVideoUrl} />
            <Timeline videos={videos} onSelect={setSelectedVideoUrl} currentUrl={selectedVideoUrl} />
            
            <h2>Eventos Inteligentes de Hoje:</h2>
            <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fill, minmax(200px, 1fr))', gap: '0.5rem' }}>
              {videos.map(v => (
                <button 
                  key={v.id} 
                  onClick={() => setSelectedVideoUrl(v.url)}
                  style={{ 
                    padding: '0.5rem', 
                    background: selectedVideoUrl === v.url ? 'var(--accent-color)' : 'var(--panel-bg)',
                    color: 'white',
                    border: '1px solid',
                    borderColor: getDetectionColor(v.label),
                    borderRadius: '4px',
                    cursor: 'pointer',
                    display: 'flex',
                    flexDirection: 'column',
                    alignItems: 'center'
                  }}
                >
                  <span style={{ fontWeight: 'bold' }}>
                    {v.label === 'video' ? 'Gravação' : `Deteção: ${v.label.toUpperCase()}`}
                  </span>
                  <span>{new Date(v.timestamp).toLocaleTimeString()}</span>
                </button>
              ))}
            </div>
          </div>
        )}
      </main>
    </div>
  )
}

export default App
