export const VideoPlayer = ({ url, type }: { url: string | null, type?: string }) => {
  if (!url) return <div style={{ height: '300px', background: '#000', display: 'flex', alignItems: 'center', justifyContent: 'center' }}>Selecione um evento</div>
  
  if (type === 'live') {
    return (
      <div style={{ width: '100%', background: '#000', borderRadius: '8px', overflow: 'hidden', position: 'relative' }}>
        <img 
          src={url} 
          alt="Live Stream" 
          key={url}
          style={{ width: '100%', display: 'block' }} 
          onError={(e) => {
            const target = e.target as HTMLImageElement;
            target.style.display = 'none';
            const parent = target.parentElement;
            if (parent) {
              const errorMsg = document.createElement('div');
              errorMsg.style.height = '300px';
              errorMsg.style.display = 'flex';
              errorMsg.style.alignItems = 'center';
              errorMsg.style.justifyContent = 'center';
              errorMsg.style.color = 'white';
              errorMsg.style.background = '#333';
              errorMsg.innerText = 'Erro ao carregar stream em direto';
              parent.appendChild(errorMsg);
            }
          }}
        />
        <div style={{ 
          position: 'absolute', 
          top: '10px', 
          left: '10px', 
          background: 'rgba(255,0,0,0.7)', 
          color: 'white', 
          padding: '2px 8px', 
          borderRadius: '4px',
          fontSize: '0.8rem',
          fontWeight: 'bold'
        }}>
          DIRETO
        </div>
      </div>
    )
  }

  if (type === 'snapshot' || url.match(/\.(jpg|jpeg|png)$/i)) {
    return (
      <div style={{ width: '100%', background: '#000', borderRadius: '8px', overflow: 'hidden' }}>
        <img src={url} alt="Snapshot" style={{ width: '100%', display: 'block' }} />
      </div>
    )
  }

  return (
    <video controls width="100%" autoPlay key={url} style={{ borderRadius: '8px' }}>
      <source src={url} type="video/mp4" />
    </video>
  )
}
