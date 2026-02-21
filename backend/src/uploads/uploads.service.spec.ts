import { ConfigService } from '@nestjs/config';
import { UploadsService } from './uploads.service';

describe('UploadsService', () => {
  it('deve retornar placeholder quando S3 nao configurado', async () => {
    const config = new ConfigService({});
    const service = new UploadsService(config);

    const result = await service.presignPhoto({
      fileName: 'foto.jpg',
      contentType: 'image/jpeg',
    });

    expect(result.provider).toBe('placeholder');
    expect(result.uploadUrl).toBeNull();
    expect(result.publicUrl).toContain('s3-placeholder.local');
  });
});
