export const VideoPlayer = ({ url }: { url: string | null }) => {
  if (!url) return <div style={{ height: '300px', background: '#000' }}>Selecione um vídeo</div>
  return (
    <video controls width="100%" key={url}>
      <source src={url} type="video/mp4" />
    </video>
  )
}
