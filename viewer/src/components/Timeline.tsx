import { getDetectionColor } from '../utils/colors';

export const Timeline = ({ videos, onSelect, currentUrl }: { 
  videos: any[], 
  onSelect: (video: any) => void,
  currentUrl: string | null 
}) => {
  return (
    <div style={{ display: 'flex', gap: '4px', height: '50px', background: 'var(--panel-bg)', padding: '5px', overflowX: 'auto', borderRadius: '8px' }}>
      {videos.map(v => {
        const url = v.video_url || v.snapshot_url;
        const isActive = currentUrl === url;
        return (
          <div 
            key={v.id}
            onClick={() => onSelect(v)}
            style={{ 
              minWidth: '20px', 
              background: isActive 
                ? 'var(--accent-color)' 
                : getDetectionColor(v.label),
              cursor: 'pointer',
              height: '100%',
              borderRadius: '4px',
              border: isActive ? '2px solid white' : 'none',
              transition: 'transform 0.1s'
            }}
            title={new Date(v.timestamp).toLocaleTimeString()}
          />
        )
      })}
    </div>
  )
}
