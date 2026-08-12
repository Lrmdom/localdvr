import { useState, useEffect } from 'react'
import { CameraSelector } from './components/CameraSelector'
import { VideoPlayer } from './components/VideoPlayer'
import { Timeline } from './components/Timeline'
import { AccessManagement } from './components/AccessManagement'
import { getDetectionColor } from './utils/colors'

function App() {
  const [cameras, setCameras] = useState<string[]>([])
  const [selectedCamera, setSelectedCamera] = useState<string>('')
  const [videos, setVideos] = useState<any[]>([])
  const [selectedVideo, setSelectedVideo] = useState<any | null>(null)
  const [view, setView] = useState<'cameras' | 'access'>('cameras')

  const selectedVideoUrl = selectedVideo?.url || null

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
        .then(data => {
          setVideos(data)
          // Ao selecionar uma câmara, o Direto é o padrão
          setSelectedVideo({
            id: 'live',
            type: 'live',
            url: `/api/live/${selectedCamera}?v=${Date.now()}`,
            label: 'direto'
          })
        })
    }
  }, [selectedCamera])

  const handleMove = (direction: string) => {
    fetch('/api/ptz/move', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ camera: selectedCamera, direction })
    })
  }

  return (
    <div style={{ display: 'grid', gridTemplateColumns: '250px 1fr', height: '100vh', gap: '1rem' }}>
      <div style={{ display: 'flex', flexDirection: 'column', background: 'var(--panel-bg)', borderRight: '1px solid #333' }}>
        <nav style={{ padding: '1rem', display: 'flex', flexDirection: 'column', gap: '0.5rem' }}>
          <button 
            onClick={() => setView('cameras')}
            style={{
              padding: '0.8rem',
              background: view === 'cameras' ? 'var(--accent-color)' : 'transparent',
              color: 'white',
              border: 'none',
              borderRadius: '4px',
              cursor: 'pointer',
              textAlign: 'left'
            }}
          >
            📹 Câmaras
          </button>
          <button 
            onClick={() => setView('access')}
            style={{
              padding: '0.8rem',
              background: view === 'access' ? 'var(--accent-color)' : 'transparent',
              color: 'white',
              border: 'none',
              borderRadius: '4px',
              cursor: 'pointer',
              textAlign: 'left'
            }}
          >
            🔑 Gestão de Acesso
          </button>
        </nav>
        
        {view === 'cameras' && <CameraSelector cameras={cameras} onSelect={setSelectedCamera} />}
      </div>

      <main style={{ padding: '1rem', overflowY: 'auto' }}>
        <h1 style={{ margin: '0 0 1rem 0' }}>LocalDVR Viewer</h1>
        
        {view === 'cameras' ? (
          <>
            {selectedCamera && (
              <div style={{ display: 'flex', flexDirection: 'column', gap: '1rem' }}>
                <div style={{ position: 'relative' }}>
                  <VideoPlayer url={selectedVideoUrl} type={selectedVideo?.type} />
                  
                  {selectedCamera === 'lsc_rotativa' && selectedVideo?.type === 'live' && (
                    <div style={{ 
                      position: 'absolute', 
                      bottom: '20px', 
                      right: '20px', 
                      display: 'grid', 
                      gridTemplateColumns: 'repeat(3, 40px)', 
                      gap: '5px',
                      background: 'rgba(0,0,0,0.5)',
                      padding: '10px',
                      borderRadius: '8px'
                    }}>
                      <div />
                      <button onClick={() => handleMove('up')} style={{ padding: '5px' }}>↑</button>
                      <div />
                      <button onClick={() => handleMove('left')} style={{ padding: '5px' }}>←</button>
                      <button onClick={() => handleMove('stop')} style={{ padding: '5px', background: 'red' }}>■</button>
                      <button onClick={() => handleMove('right')} style={{ padding: '5px' }}>→</button>
                      <div />
                      <button onClick={() => handleMove('down')} style={{ padding: '5px' }}>↓</button>
                    </div>
                  )}
                </div>
                <Timeline videos={videos} onSelect={(url) => setSelectedVideo(videos.find(v => v.url === url))} currentUrl={selectedVideoUrl} />
                
                <h2>Eventos Inteligentes de Hoje:</h2>
                <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fill, minmax(200px, 1fr))', gap: '0.5rem' }}>
                  <button 
                    onClick={() => {
                      setSelectedVideo({
                        id: 'live',
                        type: 'live',
                        url: `/api/live/${selectedCamera}?v=${Date.now()}`,
                        label: 'direto'
                      })
                    }}
                    style={{ 
                      padding: '0.5rem', 
                      background: selectedVideo?.type === 'live' ? 'var(--accent-color)' : 'var(--panel-bg)',
                      color: 'white',
                      border: '1px solid #666',
                      borderRadius: '4px',
                      cursor: 'pointer',
                      display: 'flex',
                      flexDirection: 'column',
                      alignItems: 'center',
                      minHeight: '100px',
                      justifyContent: 'center'
                    }}
                  >
                    <div style={{ fontSize: '2rem', marginBottom: '5px' }}>🔴</div>
                    <span style={{ fontWeight: 'bold' }}>DIRETO</span>
                    <span style={{ fontSize: '0.7rem' }}>Em Tempo Real</span>
                  </button>

                  {videos.map(v => (
                    <button 
                      key={v.id} 
                      onClick={() => setSelectedVideo(v)}
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
                        alignItems: 'center',
                        position: 'relative',
                        minHeight: '100px',
                        justifyContent: 'center'
                      }}
                    >
                      {v.type === 'snapshot' ? (
                        <img src={v.url} alt="Thumbnail" style={{ width: '100%', height: '60px', objectFit: 'cover', borderRadius: '2px', marginBottom: '4px' }} />
                      ) : (
                        <div style={{ height: '60px', display: 'flex', alignItems: 'center' }}>🎬</div>
                      )}
                      <span style={{ fontWeight: 'bold', fontSize: '0.8rem' }}>
                        {v.label === 'video' ? 'Gravação' : v.label.toUpperCase()}
                      </span>
                      <span style={{ fontSize: '0.7rem' }}>{v.time}</span>
                    </button>
                  ))}
                </div>
              </div>
            )}
          </>
        ) : (
          <AccessManagement />
        )}
      </main>
    </div>
  )
}

export default App
