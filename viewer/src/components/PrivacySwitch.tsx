import { useState } from 'react';

export const PrivacySwitch = ({ camera }: { camera: string }) => {
  const [isPrivacyOn, setIsPrivacyOn] = useState(false);
  const [loading, setLoading] = useState(false);

  const togglePrivacy = async () => {
    setLoading(true);
    try {
      const response = await fetch('/api/privacy/toggle', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ camera, enabled: !isPrivacyOn })
      });
      if (response.ok) {
        setIsPrivacyOn(!isPrivacyOn);
      }
    } catch (error) {
      console.error('Erro ao alternar modo privacidade:', error);
    } finally {
      setLoading(false);
    }
  };

  return (
    <button
      onClick={togglePrivacy}
      disabled={loading}
      style={{
        padding: '0.5rem 1rem',
        background: isPrivacyOn ? '#e74c3c' : '#2ecc71',
        color: 'white',
        border: 'none',
        borderRadius: '4px',
        cursor: loading ? 'not-allowed' : 'pointer',
        fontSize: '0.8rem',
        fontWeight: 'bold'
      }}
    >
      {loading ? '...' : isPrivacyOn ? '🛡️ Privacidade ATIVA' : '👁️ Privacidade INATIVA'}
    </button>
  );
};
