import * as cdk from 'aws-cdk-lib'
import * as dynamodb from 'aws-cdk-lib/aws-dynamodb'
import * as cognito from 'aws-cdk-lib/aws-cognito'
import * as lambda from 'aws-cdk-lib/aws-lambda'
import * as apigateway from 'aws-cdk-lib/aws-apigateway'
import * as s3 from 'aws-cdk-lib/aws-s3'
import * as cloudfront from 'aws-cdk-lib/aws-cloudfront'
import * as origins from 'aws-cdk-lib/aws-cloudfront-origins'
import { Construct } from 'constructs'

export class BrainboardStack extends cdk.Stack {
  constructor(scope: Construct, id: string, props?: cdk.StackProps) {
    super(scope, id, props)

    // DynamoDB Tables
    const remindersTable = new dynamodb.Table(this, 'RemindersTable', {
      tableName: 'brainboard-reminders',
      partitionKey: { name: 'user_id', type: dynamodb.AttributeType.STRING },
      sortKey: { name: 'reminder_id', type: dynamodb.AttributeType.STRING },
      billingMode: dynamodb.BillingMode.PAY_PER_REQUEST,
      removalPolicy: cdk.RemovalPolicy.DESTROY, // For development
    })

    const summariesTable = new dynamodb.Table(this, 'SummariesTable', {
      tableName: 'brainboard-summaries',
      partitionKey: { name: 'user_id', type: dynamodb.AttributeType.STRING },
      sortKey: { name: 'summary_id', type: dynamodb.AttributeType.STRING },
      billingMode: dynamodb.BillingMode.PAY_PER_REQUEST,
      removalPolicy: cdk.RemovalPolicy.DESTROY,
    })

    const usersTable = new dynamodb.Table(this, 'UsersTable', {
      tableName: 'brainboard-users',
      partitionKey: { name: 'user_id', type: dynamodb.AttributeType.STRING },
      billingMode: dynamodb.BillingMode.PAY_PER_REQUEST,
      removalPolicy: cdk.RemovalPolicy.DESTROY,
    })

    // Cognito User Pool
    const userPool = new cognito.UserPool(this, 'BrainboardUserPool', {
      userPoolName: 'brainboard-users',
      selfSignUpEnabled: true,
      userVerification: {
        emailSubject: 'Verify your email for Brainboard',
        emailBody: 'Hello {username}, Thanks for signing up to Brainboard! Your verification code is {####}',
        emailStyle: cognito.VerificationEmailStyle.CODE,
      },
      signInAliases: {
        email: true,
      },
      autoVerify: {
        email: true,
      },
      passwordPolicy: {
        minLength: 8,
        requireLowercase: true,
        requireUppercase: true,
        requireDigits: true,
        requireSymbols: false,
      },
      removalPolicy: cdk.RemovalPolicy.DESTROY,
    })

    const userPoolClient = new cognito.UserPoolClient(this, 'BrainboardUserPoolClient', {
      userPool,
      userPoolClientName: 'brainboard-web-client',
      authFlows: {
        userPassword: true,
        userSrp: true,
      },
      generateSecret: false, // For web clients
    })

    // Lambda function for the API
    const apiLambda = new lambda.Function(this, 'BrainboardApiLambda', {
      runtime: lambda.Runtime.PYTHON_3_11,
      handler: 'main.handler',
      code: lambda.Code.fromAsset('../apps/backend'),
      environment: {
        DYNAMODB_TABLE_REMINDERS: remindersTable.tableName,
        DYNAMODB_TABLE_SUMMARIES: summariesTable.tableName,
        DYNAMODB_TABLE_USERS: usersTable.tableName,
        COGNITO_USER_POOL_ID: userPool.userPoolId,
        COGNITO_CLIENT_ID: userPoolClient.userPoolClientId,
      },
      timeout: cdk.Duration.seconds(30),
    })

    // Grant Lambda permissions to access DynamoDB tables
    remindersTable.grantReadWriteData(apiLambda)
    summariesTable.grantReadWriteData(apiLambda)
    usersTable.grantReadWriteData(apiLambda)

    // API Gateway
    const api = new apigateway.LambdaRestApi(this, 'BrainboardApi', {
      handler: apiLambda,
      restApiName: 'Brainboard API',
      description: 'API for Brainboard application',
      proxy: false,
      defaultCorsPreflightOptions: {
        allowOrigins: apigateway.Cors.ALL_ORIGINS,
        allowMethods: apigateway.Cors.ALL_METHODS,
        allowHeaders: ['Content-Type', 'X-Amz-Date', 'Authorization', 'X-Api-Key'],
      },
    })

    // API Routes
    const apiResource = api.root.addResource('api')
    
    // Auth routes
    const authResource = apiResource.addResource('auth')
    authResource.addMethod('ANY')
    
    // Reminders routes
    const remindersResource = apiResource.addResource('reminders')
    remindersResource.addMethod('ANY')
    
    // Summaries routes
    const summariesResource = apiResource.addResource('summaries')
    summariesResource.addMethod('ANY')

    // S3 bucket for frontend hosting
    const frontendBucket = new s3.Bucket(this, 'BrainboardFrontendBucket', {
      bucketName: `brainboard-frontend-${this.account}`,
      websiteIndexDocument: 'index.html',
      websiteErrorDocument: 'error.html',
      publicReadAccess: true,
      blockPublicAccess: s3.BlockPublicAccess.BLOCK_ACLS,
      removalPolicy: cdk.RemovalPolicy.DESTROY,
    })

    // CloudFront distribution
    const distribution = new cloudfront.Distribution(this, 'BrainboardDistribution', {
      defaultBehavior: {
        origin: new origins.S3Origin(frontendBucket),
        viewerProtocolPolicy: cloudfront.ViewerProtocolPolicy.REDIRECT_TO_HTTPS,
        cachePolicy: cloudfront.CachePolicy.CACHING_OPTIMIZED,
      },
      errorResponses: [
        {
          httpStatus: 404,
          responseHttpStatus: 200,
          responsePagePath: '/index.html', // For SPA routing
        },
      ],
    })

    // Outputs
    new cdk.CfnOutput(this, 'UserPoolId', {
      value: userPool.userPoolId,
      description: 'Cognito User Pool ID',
    })

    new cdk.CfnOutput(this, 'UserPoolClientId', {
      value: userPoolClient.userPoolClientId,
      description: 'Cognito User Pool Client ID',
    })

    new cdk.CfnOutput(this, 'ApiEndpoint', {
      value: api.url,
      description: 'API Gateway endpoint URL',
    })

    new cdk.CfnOutput(this, 'FrontendBucketName', {
      value: frontendBucket.bucketName,
      description: 'S3 bucket name for frontend',
    })

    new cdk.CfnOutput(this, 'DistributionDomainName', {
      value: distribution.distributionDomainName,
      description: 'CloudFront distribution domain name',
    })
  }
}
