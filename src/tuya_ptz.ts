import { TuyaContext } from '@tuya/tuya-connector-nodejs';

export enum PTZDirection {
  UP = 'up',
  DOWN = 'down',
  LEFT = 'left',
  RIGHT = 'right',
  RIGHT_UP = 'right_up',
  RIGHT_DOWN = 'right_down',
  LEFT_UP = 'left_up',
  LEFT_DOWN = 'left_down',
  STOP = 'stop'
}

export class TuyaPTZService {
  private context: TuyaContext;

  constructor(baseUrl: string, accessKey: string, secretKey: string) {
    this.context = new TuyaContext({
      baseUrl,
      accessKey,
      secretKey,
    });
  }

  /**
   * Envia comando de movimento PTZ para a câmara.
   */
  async moveCamera(deviceId: string, direction: PTZDirection): Promise<boolean> {
    return this.sendPtzCommand(deviceId, direction);
  }

  /**
   * Para o movimento da câmara.
   */
  async stopCamera(deviceId: string): Promise<boolean> {
    return this.sendPtzCommand(deviceId, PTZDirection.STOP);
  }

  private async sendPtzCommand(deviceId: string, direction: PTZDirection): Promise<boolean> {
    try {
      const result = await this.context.request({
        method: 'POST',
        path: `/v1.0/cameras/${deviceId}/configs/ptz`,
        body: { value: direction },
      });

      console.log(`Comando PTZ (${direction}) enviado com sucesso para ${deviceId}`);
      return true;
    } catch (error) {
      console.error(`Erro ao enviar comando PTZ (${direction}) para ${deviceId}:`, error);
      return false;
    }
  }
}
