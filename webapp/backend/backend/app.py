#!/usr/bin/env python3
import os
import aws_cdk as cdk
from backend.backend_stack import BackendStack

app = cdk.App()


BackendStack(
    app, 
    "BackendStack",
    stage="dev",
)

app.synth()
