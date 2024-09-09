from aws_cdk import (
    Stack,
    Aws,
    aws_route53,
    aws_route53_targets,
    aws_s3,
    aws_s3_deployment,
    aws_iam,
    aws_cloudfront,
    aws_cloudfront_origins,
    aws_certificatemanager
)
from constructs import Construct

class CdkStaticwebStack(Stack):

    def __init__(self, scope: Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        domain_name = "your-domain.com"
        hosted_zone_id = <YOUR_HOSTED_ZONE_ID>
        domain_cert_name = <YOUR_DOMAIN_CERT_NAME>

        hosted_zone = aws_route53.HostedZone.from_hosted_zone_attributes(self, "WebHostedZone",
            zone_name=domain_name,
            hosted_zone_id=hosted_zone_id
        )
        arn_cert = f"arn:aws:acm:{Aws.REGION}:{Aws.ACCOUNT_ID}:certificate/{domain_cert_name}"

        domain_cert = aws_certificatemanager.Certificate.from_certificate_arn(self, "DomainCert",
            certificate_arn=arn_cert
        )
        web_bucket = aws_s3.Bucket(self, "WebBucket",
            bucket_name=domain_name,
            block_public_access=aws_s3.BlockPublicAccess(block_public_policy=False),
            website_index_document="index.html"
        )
        policy_statement = {
            "Sid": "PublicReadGetObject",
            "Effect": "Allow",
            "Principal": "*",
            "Action": ["s3:GetObject"],
            "Resource": [f"{web_bucket.bucket_arn}/*"]
        }
        web_bucket.add_to_resource_policy(aws_iam.PolicyStatement.from_json(policy_statement))

        aws_s3_deployment.BucketDeployment(self, "DeployFiles",
            sources=[aws_s3_deployment.Source.asset("./static-page")],
            destination_bucket=web_bucket
        )

        web_distribution = aws_cloudfront.Distribution(self, "WebDistro",
            enable_ipv6=True,
            default_root_object="index.html",
            domain_names=[domain_name, f"www.{domain_name}"],
            certificate=domain_cert,
            http_version=aws_cloudfront.HttpVersion.HTTP2_AND_3,
            default_behavior=aws_cloudfront.BehaviorOptions(
                origin=aws_cloudfront_origins.S3Origin(web_bucket)
            )
        )
        aws_route53.ARecord(self, "DomainIp4",
            zone=hosted_zone,
            target=aws_route53.RecordTarget.from_alias(
                alias_target=aws_route53_targets.CloudFrontTarget(web_distribution)
            )
        )
        aws_route53.ARecord(self, "wwwDomainIp4",
            record_name="www",
            zone=hosted_zone,
            target=aws_route53.RecordTarget.from_alias(
                alias_target=aws_route53_targets.CloudFrontTarget(web_distribution)
            )
        )
        aws_route53.AaaaRecord(self, "DomainIp6",
            zone=hosted_zone,
            target=aws_route53.RecordTarget.from_alias(
                alias_target=aws_route53_targets.CloudFrontTarget(web_distribution)
            )
        )
        aws_route53.AaaaRecord(self, "wwwDomainIp6",
            record_name="www",
            zone=hosted_zone,
            target=aws_route53.RecordTarget.from_alias(
                alias_target=aws_route53_targets.CloudFrontTarget(web_distribution)
            )
        )