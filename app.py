#!/usr/bin/env python3
import aws_cdk as cdk
from cdk_staticweb.cdk_staticweb_stack import CdkStaticwebStack

app = cdk.App()
CdkStaticwebStack(app, "CdkStaticwebStack", synthesizer=cdk.DefaultStackSynthesizer(generate_bootstrap_version_rule=False))
app.synth()
