import { useState, useEffect } from 'react'

export const AccessManagement = () => {
  const [status, setStatus] = useState<any>(null)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const [inviteUrl, setInviteUrl] = useState<string | null>(null)
  const [users, setUsers] = useState<any[]>([])
  const joinedUsers = users.filter(u => u.displayName || u.loginName)
  const pendingUsers = users.filter(u => !u.displayName && !u.loginName)

  const fetchStatus = async () => {
    try {
      const res = await fetch('/api/access/status')
      const data = await res.json()
      setStatus(data)
    } catch (err) {
      setError('Erro ao ligar ao servidor')
    }
  }

  const fetchUsers = async () => {
    try {
      const res = await fetch('/api/access/users')
      const data = await res.json()
      setUsers(data)
    } catch (err) {
      console.error('Erro ao buscar utilizadores', err)
    }
  }

  useEffect(() => {
    fetchStatus()
    fetchUsers()
  }, [])

  const generateInvite = async () => {
    setLoading(true)
    setError(null)
    setInviteUrl(null)
    try {
      const res = await fetch('/api/access/invite', { method: 'POST' })
      const data = await res.json()
      if (data.error) {
        setError(data.error)
      } else {
        setInviteUrl(data.inviteUrl || data.url || 'Link gerado com sucesso!')
        fetchStatus()
      }
    } catch (err) {
      setError('Erro ao gerar convite')
    }
    setLoading(false)
  }

  if (!status) return <div>A carregar definições de acesso...</div>

  return (
    <div style={{ padding: '1rem', background: 'var(--panel-bg)', borderRadius: '8px', marginTop: '1rem' }}>
      <h2>Gestão de Acesso (Tailscale)</h2>
      
      {!status.configured ? (
        <div style={{ color: '#ff4444', marginBottom: '1rem' }}>
          <strong>Configuração Pendente:</strong> {status.reason}
          <p style={{ fontSize: '0.9rem', color: '#ccc' }}>
            Adicione <code>TS_API_KEY</code> ao seu ficheiro <code>.env</code> para ativar esta funcionalidade.
          </p>
        </div>
      ) : (
        <div>
          <p>O seu servidor está seguro e isolado no Docker.</p>
          
          <div style={{ marginBottom: '2rem' }}>
            <button 
              onClick={generateInvite} 
              disabled={loading}
              style={{
                padding: '0.8rem 1.5rem',
                background: '#2c3e50',
                color: 'white',
                border: '1px solid #34495e',
                borderRadius: '4px',
                cursor: loading ? 'not-allowed' : 'pointer',
                fontWeight: 'bold'
              }}
            >
              {loading ? 'A gerar...' : '➕ Convidar Novo Utilizador'}
            </button>
            
            {error && <p style={{ color: '#ff4444', marginTop: '0.5rem' }}>{error}</p>}
            
            {inviteUrl && (
              <div style={{ marginTop: '1rem', padding: '1rem', background: '#27ae60', borderRadius: '4px' }}>
                <p style={{ margin: 0 }}><strong>1. Link de Convite (Tailscale):</strong></p>
                <code style={{ display: 'block', wordBreak: 'break-all', margin: '0.5rem 0', color: 'white', background: 'rgba(0,0,0,0.2)', padding: '5px' }}>{inviteUrl}</code>
                
                <p style={{ margin: '10px 0 0 0' }}><strong>2. Endereço do Viewer:</strong></p>
                <code style={{ display: 'block', margin: '0.5rem 0', color: 'white', background: 'rgba(0,0,0,0.2)', padding: '5px' }}>http://100.71.180.27</code>
                
                <div style={{ marginTop: '10px', fontSize: '0.85rem', borderTop: '1px solid rgba(255,255,255,0.2)', paddingTop: '10px' }}>
                  <strong>Instruções para o convidado:</strong>
                  <ol style={{ paddingLeft: '20px', marginTop: '5px' }}>
                    <li>Clicar no Link 1 e aceitar o convite (instalar App Tailscale).</li>
                    <li>Ligar a App Tailscale no telemóvel/PC.</li>
                    <li>Abrir o navegador e entrar no Link 2.</li>
                  </ol>
                </div>
              </div>
            )}
          </div>

          <h3>Utilizadores do Tailnet:</h3>
          {users && users.length > 0 ? (
            <ul style={{ listStyle: 'none', padding: 0 }}>
              {users.map((user: any, idx: number) => {
                const isPending = !user.displayName && !user.loginName;
                const isOwner = user.role === 'owner';
                const status = user.status || (isPending ? 'Pendente' : 'Ativo');

                return (
                  <li key={idx} style={{ 
                    padding: '0.8rem', 
                    borderBottom: '1px solid #444',
                    background: isPending ? 'rgba(255,255,0,0.05)' : 'rgba(255,255,255,0.05)',
                    marginBottom: '0.5rem',
                    borderRadius: '4px'
                  }}>
                    <div style={{ display: 'flex', justifyContent: 'space-between' }}>
                      <div style={{ fontWeight: 'bold', fontSize: '1.1rem', color: '#fff' }}>
                        {isPending ? '⏳ Convite Pendente' : (user.displayName || 'Utilizador')}
                      </div>
                      <div style={{ fontSize: '0.8rem', color: isOwner ? '#f1c40f' : '#aaa', textTransform: 'uppercase' }}>
                        {user.role}
                      </div>
                    </div>
                    <div style={{ fontSize: '0.9rem', color: '#aaa', marginTop: '2px' }}>
                      {user.loginName || `ID: ${user.id}`}
                    </div>
                    <div style={{ fontSize: '0.8rem', color: user.currentlyConnected ? '#2ecc71' : '#5dade2', marginTop: '4px' }}>
                      {user.currentlyConnected ? '🟢 Connected' : 
                       user.lastSeen ? `Last seen: ${new Date(user.lastSeen).toLocaleString()}` : 'Status desconhecido'}
                    </div>
                  </li>
                );
              })}
            </ul>
          ) : (
            <p style={{ color: '#888' }}>Sem utilizadores no Tailnet.</p>
          )}

          <h3>Partilhas de Dispositivo (Shares):</h3>
          {status.active_shares && status.active_shares.length > 0 ? (
            <ul style={{ listStyle: 'none', padding: 0 }}>
              {status.active_shares.map((share: any, idx: number) => (
                <li key={idx} style={{ padding: '0.5rem 0', borderBottom: '1px solid #333' }}>
                  👤 {share.to || 'Utilizador Partilhado'} 
                  <span style={{ float: 'right', fontSize: '0.8rem', color: '#888' }}>
                    {share.created ? new Date(share.created).toLocaleDateString() : 'Ativo'}
                  </span>
                </li>
              ))}
            </ul>
          ) : (
            <p style={{ color: '#888' }}>Ainda não partilhou o acesso com ninguém.</p>
          )}
        </div>
      )}
    </div>
  )
}
