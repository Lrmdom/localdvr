import { TuyaPTZService, PTZDirection } from './tuya_ptz';
import * as dotenv from 'dotenv';

dotenv.config();

const { TUYA_CLIENT_ID, TUYA_CLIENT_SECRET, TUYA_ENDPOINT } = process.env;

if (!TUYA_CLIENT_ID || !TUYA_CLIENT_SECRET || !TUYA_ENDPOINT) {
  console.error('Credenciais Tuya ausentes nas variáveis de ambiente.');
  process.exit(1);
}

const ptzService = new TuyaPTZService(TUYA_ENDPOINT, TUYA_CLIENT_ID, TUYA_CLIENT_SECRET);

// Exemplo de uso
async function runExample() {
  const deviceId = 'vdevo123456789'; // Substituir pelo ID real da câmara

  console.log('Movendo câmara...');
  const moved = await ptzService.moveCamera(deviceId, PTZDirection.UP);
  
  if (moved) {
    console.log('Aguardando...');
    await new Promise(resolve => setTimeout(resolve, 1000));
    await ptzService.stopCamera(deviceId);
    console.log('Câmara parada.');
  }
}

runExample();
