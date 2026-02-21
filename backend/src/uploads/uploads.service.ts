import { PutObjectCommand, S3Client } from '@aws-sdk/client-s3';
import { getSignedUrl } from '@aws-sdk/s3-request-presigner';
import { BadRequestException, Injectable } from '@nestjs/common';
import { ConfigService } from '@nestjs/config';
import { PresignPhotoDto } from './dto/presign-photo.dto';

@Injectable()
export class UploadsService {
  constructor(private readonly config: ConfigService) {}

  private getS3Config() {
    const bucket = this.config.get<string>('S3_BUCKET');
    const endpoint = this.config.get<string>('S3_ENDPOINT');
    const region = this.config.get<string>('S3_REGION') ?? 'us-east-1';
    const accessKeyId = this.config.get<string>('S3_ACCESS_KEY_ID');
    const secretAccessKey = this.config.get<string>('S3_SECRET_ACCESS_KEY');
    const publicBaseUrl = this.config.get<string>('S3_PUBLIC_BASE_URL');
    return { bucket, endpoint, region, accessKeyId, secretAccessKey, publicBaseUrl };
  }

  async uploadPhotoBuffer(file: {
    originalname: string;
    mimetype: string;
    buffer: Buffer;
  }) {
    if (!file?.buffer?.length) {
      throw new BadRequestException('Arquivo de foto obrigatorio.');
    }
    const {
      bucket,
      endpoint,
      region,
      accessKeyId,
      secretAccessKey,
      publicBaseUrl,
    } = this.getS3Config();
    const objectKey = `returns/${Date.now()}-${file.originalname}`;

    if (!bucket || !endpoint || !accessKeyId || !secretAccessKey) {
      return {
        provider: 'placeholder',
        objectKey,
        publicUrl: `https://s3-placeholder.local/${objectKey}`,
      };
    }

    const s3 = new S3Client({
      region,
      endpoint,
      credentials: { accessKeyId, secretAccessKey },
      forcePathStyle: true,
    });

    await s3.send(
      new PutObjectCommand({
        Bucket: bucket,
        Key: objectKey,
        ContentType: file.mimetype || 'image/jpeg',
        Body: file.buffer,
      }),
    );

    return {
      provider: 's3',
      objectKey,
      publicUrl: publicBaseUrl
        ? `${publicBaseUrl}/${objectKey}`
        : `${endpoint}/${bucket}/${objectKey}`,
    };
  }

  async presignPhoto(dto: PresignPhotoDto) {
    const { bucket, endpoint, region, accessKeyId, secretAccessKey, publicBaseUrl } =
      this.getS3Config();

    const objectKey = `returns/${Date.now()}-${dto.fileName}`;

    if (!bucket || !endpoint || !accessKeyId || !secretAccessKey) {
      return {
        provider: 'placeholder',
        uploadUrl: null,
        objectKey,
        publicUrl: `https://s3-placeholder.local/${objectKey}`,
      };
    }

    const s3 = new S3Client({
      region,
      endpoint,
      credentials: { accessKeyId, secretAccessKey },
      forcePathStyle: true,
    });

    const command = new PutObjectCommand({
      Bucket: bucket,
      Key: objectKey,
      ContentType: dto.contentType ?? 'image/jpeg',
    });

    const uploadUrl = await getSignedUrl(s3, command, { expiresIn: 60 * 5 });
    const publicUrl = publicBaseUrl
      ? `${publicBaseUrl}/${objectKey}`
      : `${endpoint}/${bucket}/${objectKey}`;

    return {
      provider: 's3',
      uploadUrl,
      objectKey,
      publicUrl,
    };
  }
}
