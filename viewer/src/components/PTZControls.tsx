export const PTZControls = ({ camera }: { camera: string }) => {
  const move = async (direction: string) => {
    try {
      await fetch(`/api/ptz/move?camera=${camera}&direction=${direction}`, { method: 'POST' });
    } catch (err) {
      console.error('PTZ Error:', err);
    }
  };

  return (
    <div style={{ 
      display: 'grid', 
      gridTemplateColumns: 'repeat(3, 1fr)', 
      gap: '10px', 
      width: '150px', 
      margin: '10px auto',
      background: 'rgba(0,0,0,0.5)',
      padding: '10px',
      borderRadius: '8px'
    }}>
      <div />
      <button onClick={() => move('up')} style={btnStyle}>▲</button>
      <div />
      
      <button onClick={() => move('left')} style={btnStyle}>◀</button>
      <button onClick={() => move('stop')} style={{...btnStyle, background: '#c0392b'}}>■</button>
      <button onClick={() => move('right')} style={btnStyle}>▶</button>
      
      <div />
      <button onClick={() => move('down')} style={btnStyle}>▼</button>
      <div />
    </div>
  );
};

const btnStyle = {
  padding: '10px',
  background: '#2c3e50',
  color: 'white',
  border: 'none',
  borderRadius: '4px',
  cursor: 'pointer',
  fontSize: '18px'
};
