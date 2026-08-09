export const CameraSelector = ({ cameras, onSelect }: { cameras: string[], onSelect: (name: string) => void }) => (
  <aside style={{ background: 'var(--panel-bg)', padding: '1rem', borderRight: '1px solid var(--border-color)', display: 'flex', flexDirection: 'column', gap: '0.5rem' }}>
    <h3 style={{ marginTop: 0 }}>Câmaras</h3>
    {cameras.map(cam => (
      <button 
        key={cam} 
        onClick={() => onSelect(cam)}
        style={{ padding: '0.5rem', cursor: 'pointer', background: '#333', color: 'white', border: 'none' }}
      >
        {cam}
      </button>
    ))}
  </aside>
)
