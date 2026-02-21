import {
  Body,
  Controller,
  Post,
  UploadedFile,
  UseGuards,
  UseInterceptors,
} from '@nestjs/common';
import { UserRole } from '@prisma/client';
import { FileInterceptor } from '@nestjs/platform-express';
import { AuthenticatedGuard } from '../auth/authenticated.guard';
import { Roles } from '../auth/roles.decorator';
import { RolesGuard } from '../auth/roles.guard';
import { PresignPhotoDto } from './dto/presign-photo.dto';
import { UploadsService } from './uploads.service';

@Controller('uploads')
@UseGuards(AuthenticatedGuard, RolesGuard)
export class UploadsController {
  constructor(private readonly uploadsService: UploadsService) {}

  @Post()
  @UseInterceptors(FileInterceptor('file'))
  @Roles(
    UserRole.ADMIN,
    UserRole.ADMINISTRATIVE,
    UserRole.MANAGER,
    UserRole.OPERATOR,
  )
  uploadPhoto(
    @UploadedFile()
    file: { originalname: string; mimetype: string; buffer: Buffer },
  ) {
    return this.uploadsService.uploadPhotoBuffer(file);
  }

  @Post('photo/presign')
  @Roles(
    UserRole.ADMIN,
    UserRole.ADMINISTRATIVE,
    UserRole.MANAGER,
    UserRole.OPERATOR,
  )
  presignPhoto(@Body() body: PresignPhotoDto) {
    return this.uploadsService.presignPhoto(body);
  }
}
