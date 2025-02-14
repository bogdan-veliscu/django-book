# Conduit API

A Medium clone built with Django REST Framework. This implementation uses modern Python tools and practices to create a robust backend service for the blog platform.

## Features

- User authentication and authorization
- Article creation and management
- Comment system
- User profiles
- Tagging system
- Real-time updates
- API documentation

## Technology Stack

- Python 3.12
- Django 5.0
- Django REST Framework
- PostgreSQL
- Docker & Docker Compose
- UV for package management
- Ruff for linting
- pytest for testing

## Development Setup

1. Clone the repository
2. Install dependencies:
   ```bash
   uv venv
   source .venv/bin/activate
   uv pip install -e ".[dev]"
   ```

3. Run migrations:
   ```bash
   python manage.py migrate
   ```

4. Start the development server:
   ```bash
   python manage.py runserver
   ```

## Production Deployment

Use Docker Compose:

```bash
docker compose -f docker-compose.prod.yml up -d
```

## Testing

Run tests with:

```bash
pytest
```

## License

MIT License

# AWS Bucket setup

Here's how you can create and configure an S3 bucket named `brandfocus` in the `eu-west-1` region using the AWS CLI:

### Step 1: Create the S3 Bucket

Run the following command to create the S3 bucket named `brandfocus` in the `eu-west-1` region:

```bash
aws s3api create-bucket --bucket brandfocus --region eu-west-1 --create-bucket-configuration LocationConstraint=eu-west-1
```

### Step 2: Configure Bucket Public Access (Optional)

If you want your S3 bucket to be publicly accessible, update the bucket's public access settings with this command:

```bash
aws s3api put-public-access-block --bucket brandfocus --public-access-block-configuration BlockPublicAcls=false,IgnorePublicAcls=false,BlockPublicPolicy=false,RestrictPublicBuckets=false
```

### Step 3: Set Up Bucket Policy for Public Access (Optional)

If you want to allow public read access to the files in the `brandfocus` bucket, create a file called `bucket-policy.json` with the following content:

```bash
aws s3api put-bucket-policy --bucket brandfocus-ai --profile codeswiftr --policy \
'{
    "Version": "2012-10-17",
    "Statement": [
        {
            "Sid": "PublicReadGetObject",
            "Effect": "Allow",
            "Principal": "*",
            "Action": "s3:GetObject",
            "Resource": "arn:aws:s3:::brandfocus-ai/*"
        }
    ]
}'
```

### Step 4: Upload Files to Your S3 Bucket

To upload files to your `brandfocus` bucket, use the following commands:

To upload a single file:

```bash
aws s3 cp /path/to/your/file s3://brandfocus/
```

To sync an entire directory:

```bash
aws s3 sync /path/to/your/directory s3://brandfocus/
```

With these steps, you've created and configured the `brandfocus` S3 bucket in the `