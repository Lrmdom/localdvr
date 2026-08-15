export const CameraSelector = ({ 
  cameras, 
  onSelect, 
  selectedCamera 
}: { 
  cameras: string[], 
  onSelect: (name: string) => void,
  selectedCamera: string
}) => (
  <aside style={{ background: 'var(--panel-bg)', padding: '1rem', borderRight: '1px solid var(--border-color)', display: 'flex', flexDirection: 'column', gap: '0.5rem' }}>
    <h3 style={{ marginTop: 0 }}>Câmaras</h3>
    {cameras.map(cam => {
      const isSelected = cam === selectedCamera;
      return (
        <button 
          key={cam} 
          onClick={() => onSelect(cam)}
          style={{ 
            padding: '0.5rem', 
            cursor: 'pointer', 
            background: isSelected ? 'var(--accent-color)' : '#333', 
            color: 'white', 
            border: isSelected ? '2px solid white' : 'none',
            fontWeight: isSelected ? 'bold' : 'normal',
            transition: 'all 0.2s'
          }}
        >
          {cam}
        </button>
      )
    })}
  </aside>
)
