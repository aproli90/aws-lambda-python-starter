# AWS Lambda Starter Kit with SAM

This repository contains a reusable starter kit for AWS Lambda functions, built with AWS SAM (Serverless Application Model), Docker, and Python 3.12. It provides a foundation for both API-driven and scheduled event-driven serverless applications.

## Features

- **Dual Lambda Function Architecture**:
  - API Function with HTTP endpoints via API Gateway
  - Event Function with scheduled cron-based triggers
- **Docker-based Deployment**: Consistent environments across development and production
- **Parameterized Infrastructure**: Easy to create multiple stacks from the same codebase
- **CI/CD with GitHub Actions**: Automated deployment pipeline
- **Comprehensive IAM Role Management**: Proper security permissions
- **Local Testing Support**: Test Lambda functions without deploying to AWS
- **AWS Secrets Manager Integration**: Secure secrets handling

## Project Structure

```
project/
├── .github/
│   └── workflows/
│       └── sam-deploy.yml    # GitHub Actions workflow for CI/CD
├── src/
│   ├── api/                  # API Lambda function
│   │   ├── app.py            # Lambda handler code
│   │   └── api_manager.py    # API business logic
│   ├── event/                # Event Lambda function
│   │   ├── app.py            # Lambda handler code
│   │   └── event_manager.py  # Event business logic
│   ├── functions/            # Business logic implementation
│   └── utils/                # Shared utilities
│       └── secrets_manager.py # AWS Secrets Manager integration
├── events/                   # Sample event files for testing
├── template.yaml             # SAM template for main resources
├── iam-role.yaml             # IAM role definition
├── scripts/
│   └── sam-commands.ps1      # Helper PowerShell script
├── Dockerfile                # Docker configuration for Lambda
├── requirements.txt          # Python dependencies
└── README.md
```

## Lambda Functions

1. **API Function**: HTTP endpoint accessible via API Gateway
   - Default endpoints:
     - `/hello` (GET): Simple health check
     - `/health` (GET): Application health status

2. **Event Function**: Triggered by scheduled events
   - Default schedules:
     - Every hour: Daily processing tasks
     - Every 6 hours: Data synchronization tasks

## Prerequisites

- [AWS CLI](https://aws.amazon.com/cli/)
- [AWS SAM CLI](https://docs.aws.amazon.com/serverless-application-model/latest/developerguide/serverless-sam-cli-install.html)
- [Docker](https://www.docker.com/products/docker-desktop/)
- Python 3.12
- PowerShell (for Windows)

## Using This as a Starter Kit

### 1. Clone and Customize

1. Clone this repository
2. Update the project prefix in the following places:
   - **YAML Configuration Files** (most important):
     - `template.yaml`: Update the `ProjectPrefix` parameter default value
     - `iam-role.yaml`: Update both `ProjectPrefix` and `ProjectPrefixLower` parameter default values
   - `scripts/sam-commands.ps1`: Update the default values for `$ProjectPrefix` and `$ProjectPrefixCamel`
   - `.github/workflows/sam-deploy.yml`: Update the default values for workflow inputs
   - **AWS Secrets Manager**: Ensure your secrets in AWS Secrets Manager follow the naming convention `{project-prefix}-secrets` (using the kebab-case prefix)

### 2. Customize Lambda Functions

1. **Add your business logic in the `src/functions/` directory**:
   - The functions could be reused for both API and Event functions

2. **Update the controllers to use your functions**:
   - Modify `src/api/app.py` to route requests to your API functions
   - Modify `src/event/app.py` to handle events with your event functions

3. **Note**: You typically don't need to modify the manager files (`api_manager.py` and `event_manager.py`) as they handle the core routing logic.

### 3. Update Infrastructure

1. Modify `template.yaml` to add additional resources or endpoints
2. Update `iam-role.yaml` to adjust permissions as needed
3. Add any required environment variables or parameters

## Local Development

### Build the application

```bash
.\scripts\sam-commands.ps1 build
```

### Test locally

Test the API function:
```bash
.\scripts\sam-commands.ps1 invoke-api
```

Test the Event function:
```bash
.\scripts\sam-commands.ps1 invoke-event
```

Start a local API Gateway:
```bash
.\scripts\sam-commands.ps1 start-api
```

Clean Docker resources:
```bash
.\scripts\sam-commands.ps1 clean-docker
```

### Deploy to AWS

Deploy to AWS:
```bash
.\scripts\sam-commands.ps1 deploy
```

## CI/CD with GitHub Actions

This repository includes a GitHub Actions workflow that automatically deploys the application to AWS when changes are pushed to the main branch.

### Setup CI/CD

1. Store your AWS credentials as GitHub repository secrets:
   - `AWS_ACCESS_KEY_ID`
   - `AWS_SECRET_ACCESS_KEY`
   - `AWS_REGION`

2. The IAM user whose credentials you add to GitHub secrets should have these policies attached:
   - `AmazonAPIGatewayAdministrator`
   - `AmazonAPIGatewayInvokeFullAccess`
   - `AmazonEC2ContainerRegistryFullAccess`
   - `AmazonS3FullAccess`
   - `AmazonSNSFullAccess`
   - `AWSCloudFormationFullAccess`
   - `AWSLambda_FullAccess`
   - `CloudWatchEventsFullAccess`
   - `IAMFullAccess`
   - `SecretsManagerReadWrite`

3. Push changes to the main branch to trigger the deployment.

### Custom Deployments via GitHub Actions

You can also manually trigger deployments with custom project prefixes:

1. Go to the "Actions" tab in your GitHub repository
2. Select the "Deploy SAM Application" workflow
3. Click "Run workflow"
4. Enter your desired project prefixes
5. Click "Run workflow"

## Required AWS Permissions

The deployment requires the following AWS permissions:

- IAM role creation and management
- Lambda function creation and management
- API Gateway creation and management
- CloudWatch Events/EventBridge rule creation
- ECR repository creation and management
- CloudFormation stack management
- S3 bucket access (for deployment artifacts)
- Secrets Manager access (if using the secrets manager integration)

## Best Practices

1. **Secrets Management**: Store sensitive information in AWS Secrets Manager
2. **Monitoring**: Set up CloudWatch alarms for your Lambda functions
3. **Logging**: Use structured logging for better observability

## License

See the [LICENSE](LICENSE) file for details.
