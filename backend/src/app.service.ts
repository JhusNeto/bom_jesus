import { Injectable } from '@nestjs/common';

@Injectable()
export class AppService {
  getHealth() {
    return {
      service: 'bom-jesus-operacional-api',
      status: 'ok',
      timestamp: new Date().toISOString(),
    };
  }
}
