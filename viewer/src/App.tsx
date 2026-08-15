import { useState, useEffect } from 'react'
import { CameraSelector } from './components/CameraSelector'
import { VideoPlayer } from './components/VideoPlayer'
import { Timeline } from './components/Timeline'
import { AccessManagement } from './components/AccessManagement'
import { PTZControls } from './components/PTZControls'
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

  return (
    <div className="app-container">
      <div className="sidebar">
        <nav style={{ padding: '1rem', display: 'flex', flexDirection: 'row', gap: '0.5rem' }}>
          <button 
            onClick={() => setView('cameras')}
            style={{
              padding: '1rem',
              flex: 1,
              background: view === 'cameras' ? 'var(--accent-color)' : '#444',
              color: 'white',
              border: 'none',
              borderRadius: '8px',
              cursor: 'pointer',
              fontWeight: 'bold'
            }}
          >
            📹 Câmaras
          </button>
          <button 
            onClick={() => setView('access')}
            style={{
              padding: '1rem',
              flex: 1,
              background: view === 'access' ? 'var(--accent-color)' : '#444',
              color: 'white',
              border: 'none',
              borderRadius: '8px',
              cursor: 'pointer',
              fontWeight: 'bold'
            }}
          >
            🔑 Acesso
          </button>
        </nav>
        
        {view === 'cameras' && <CameraSelector cameras={cameras} onSelect={setSelectedCamera} selectedCamera={selectedCamera} />}
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
                    <PTZControls camera={selectedCamera} />
                  )}
                </div>
                <Timeline 
                  videos={videos} 
                  onSelect={(video) => setSelectedVideo({ 
                    ...video, 
                    url: video.video_url || video.snapshot_url, 
                    type: video.video_url ? 'video' : 'snapshot' 
                  })} 
                  currentUrl={selectedVideoUrl} 
                />
                
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

                  {videos.map(v => {
                    const url = v.video_url || v.snapshot_url;
                    const type = v.video_url ? 'video' : 'snapshot';
                    return (
                      <button 
                        key={v.id} 
                        onClick={() => setSelectedVideo({ ...v, url, type })}
                        style={{ 
                          padding: '0.5rem', 
                          background: selectedVideoUrl === url ? 'var(--accent-color)' : 'var(--panel-bg)',
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
                        {v.snapshot_url ? (
                          <img src={v.snapshot_url} alt="Thumbnail" style={{ width: '100%', height: '60px', objectFit: 'cover', borderRadius: '2px', marginBottom: '4px' }} />
                        ) : (
                          <div style={{ height: '60px', display: 'flex', alignItems: 'center' }}>{v.video_url ? '🎬' : '📷'}</div>
                        )}
                        <span style={{ fontWeight: 'bold', fontSize: '0.8rem' }}>
                          {v.label.toUpperCase()}
                        </span>
                        <span style={{ fontSize: '0.7rem' }}>{v.time}</span>
                      </button>
                    )
                  })}
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
