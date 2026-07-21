resource "random_id" "lambda_bucket_suffix" {
  byte_length = 4
}

resource "aws_s3_bucket" "lambda_packages" {
  bucket = "gratitude-bot-lambda-packages-${var.environment}-${random_id.lambda_bucket_suffix.hex}"
  tags   = var.tags
}

resource "aws_s3_bucket_versioning" "lambda_packages" {
  bucket = aws_s3_bucket.lambda_packages.bucket
  versioning_configuration {
    status = "Enabled"
  }
}

resource "aws_s3_bucket_server_side_encryption_configuration" "lambda_packages" {
  bucket = aws_s3_bucket.lambda_packages.bucket
  rule {
    apply_server_side_encryption_by_default {
      sse_algorithm = "AES256"
    }
  }
}
