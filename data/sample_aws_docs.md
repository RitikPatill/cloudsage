# CloudSage sample knowledge base — AWS cost & architecture facts (verified July 2026)

## AWS Free account plan
At signup, AWS offers a Free account plan and a Paid account plan. The Free account plan
grants $100 in credits immediately plus up to $100 more ($20 per activity for trying EC2,
RDS, Lambda, Bedrock, and AWS Budgets). The Free plan lasts 6 months or until credits are
exhausted, whichever comes first. On the Free plan you can never be surprise-billed: when
credits run out or the 6 months end, AWS automatically closes the account instead of
charging you. Data can be recovered for 90 days by upgrading to a paid plan.

## Always-free serverless services (never expire, reset monthly)
AWS Lambda: 1,000,000 requests and 400,000 GB-seconds of compute per month, free forever.
Amazon DynamoDB: 25 GB of storage plus 25 read and 25 write capacity units, free forever.
AWS Step Functions: 4,000 state transitions per month. Amazon SQS and SNS: 1,000,000
requests/publishes each per month. Amazon Cognito: 10,000 monthly active users on the
Lite/Essentials tiers. Amazon CloudWatch: 10 custom metrics and 10 alarms. AWS Systems
Manager Parameter Store (Standard tier): free, and a good zero-cost alternative to AWS
Secrets Manager, which costs $0.40 per secret per month.

## Vector stores: the big cost trap
Amazon OpenSearch Serverless has a minimum charge of roughly $345 per month even when
idle, because it bills a floor of OpenSearch Compute Units. It is the number one surprise
bill for RAG hobby projects. The cheapest way to host a vector store on AWS is Amazon S3
Vectors: about $0.06 per GB-month for storage, $0.20 per GB for uploads (PUT), and about
$2.50 per million queries, with no monthly minimum. S3 Vectors integrates directly with
Amazon Bedrock Knowledge Bases. For local development, a self-hosted Qdrant container in
Docker costs nothing at all.

## Other classic beginner bill traps
A NAT Gateway costs about $32 per month plus data processing from the second it exists —
avoid it by keeping Lambdas out of a VPC, since Bedrock, S3, and DynamoDB are reachable
over public AWS APIs with IAM authentication. An EKS cluster control plane costs about
$73 per month and is never free; use a local kind or minikube cluster to learn Kubernetes
instead. Application and Network Load Balancers cost roughly $16-22 per month base; use
API Gateway HTTP APIs with Lambda instead. Idle Elastic IPs and public IPv4 addresses
bill $0.005 per hour each. Provisioned SageMaker endpoints bill hourly after the 2-month
free window — about $33 per month for a small instance left running.

## Amazon Bedrock costs
Amazon Bedrock has no free tier: it bills per token from the first API call, but small
demo usage costs pennies and is covered by Free-plan signup credits. Amazon Nova 2 Lite
is the current cheap default model; the older Nova Micro and Claude 3.5 Haiku are legacy.
Bedrock Guardrails bills per text unit on both input and output (roughly $0.15-0.25 per
1,000 text units). For EU data residency, use the EU (Geo) cross-region inference profile
pinned to eu-central-1 (Frankfurt) — never the Global profile, which may route requests
to US regions.

## Cost safety setup
Create a zero-spend budget with AWS Budgets on day one (the first two budgets are free)
and enable Free Tier usage alerts, which email you at 85% of each service's free limit.
Set CloudWatch log groups to 7-day retention so logs never silently accumulate, and run
terraform destroy on idle stacks.
