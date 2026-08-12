import { getDetectionColor } from '../utils/colors';

export const Timeline = ({ videos, onSelect, currentUrl }: { 
  videos: any[], 
  onSelect: (video: any) => void,
  currentUrl: string | null 
}) => {
  return (
    <div style={{ display: 'flex', gap: '2px', height: '40px', background: 'var(--panel-bg)', padding: '5px' }}>
      {videos.map(v => {
        const url = v.video_url || v.snapshot_url;
        return (
          <div 
            key={v.id}
            onClick={() => onSelect(v)}
            style={{ 
              width: '10px', 
              background: currentUrl === url 
                ? 'var(--accent-color)' 
                : getDetectionColor(v.label),
              cursor: 'pointer',
              height: '100%'
            }}
            title={new Date(v.timestamp).toLocaleTimeString()}
          />
        )
      })}
    </div>
  )
}
