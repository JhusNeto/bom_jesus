import { Module } from '@nestjs/common';
import { ReviewsController } from './reviews.controller';
import { ReviewsV1Controller } from './reviews-v1.controller';
import { ReviewsService } from './reviews.service';

@Module({
  controllers: [ReviewsController, ReviewsV1Controller],
  providers: [ReviewsService],
})
export class ReviewsModule {}
