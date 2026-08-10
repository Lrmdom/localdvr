export const Timeline = ({ videos, onSelect, currentUrl }: { 
  videos: any[], 
  onSelect: (url: string) => void,
  currentUrl: string | null 
}) => {
  return (
    <div style={{ display: 'flex', gap: '2px', height: '40px', background: 'var(--panel-bg)', padding: '5px' }}>
      {videos.map(v => {
        return (
          <div 
            key={v.id}
            onClick={() => onSelect(v.url)}
            style={{ 
              width: '10px', 
              background: currentUrl === v.url 
                ? 'var(--accent-color)' 
                : (v.label.toLowerCase() === 'person' ? 'orange' : v.label.toLowerCase() === 'dog' ? 'blue' : '#555'),
              cursor: 'pointer',
              height: '100%'
            }}
            title={v.time}
          />
        )
      })}
    </div>
  )
}
