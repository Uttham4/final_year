from aws_cdk import (
    Stack,
    aws_iam as iam,
    aws_events as events,
    aws_events_targets as targets,
    aws_lambda as _lambda,
    aws_apigateway as apigw,
    aws_ec2 as ec2,
    Duration
)
from constructs import Construct
import os


class BackendStack(Stack):

    def __init__(self, scope: Construct, construct_id: str, stage, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)



        self.function_prefix = construct_id.replace("-", "_")
        self.ASSET = "API"
        self.integration_responses = [{
            'statusCode': '200',
            'responseParameters': {
                'method.response.header.Access-Control-Allow-Origin': "'*'",
            }
        }] 
        self.method_responses = [{
            'statusCode': '200',
            'responseParameters': {
                'method.response.header.Access-Control-Allow-Origin': True,
            }
        }]

        env = { "stage": stage, "id": "014498663421" }



# VPC
 
        
        self.vpc = ec2.Vpc.from_vpc_attributes(self, construct_id, vpc_id="vpc-0889619d1f341d845", availability_zones=[
                                          "us-east-2"], private_subnet_ids=["subnet-0848dc6b221020b13","subnet-03a9fa9d06e6d7746","subnet-00d12a14ad24f7bbc"])


        self.security_group_1 = ec2.SecurityGroup.from_security_group_id(self, 'SG-1', 'sg-07806a5b8a59eb300')
        self.security_group_2 = ec2.SecurityGroup.from_security_group_id(self, 'SG-2', 'sg-0f06c43458391d122')

        self.security_groups = [self.security_group_1, self.security_group_2]


        mysql = _lambda.LayerVersion.from_layer_version_arn(self, 'mysql-layer','arn:aws:lambda:us-east-2:014498663421:layer:mysql-layer:1')
        jwt = _lambda.LayerVersion.from_layer_version_arn(self, 'jwt','arn:aws:lambda:us-east-2:014498663421:layer:jwt:1')
        bcrypt = _lambda.LayerVersion.from_layer_version_arn(self, 'bcrypt','arn:aws:lambda:us-east-2:014498663421:layer:bcypt:1')
        requests = _lambda.LayerVersion.from_layer_version_arn(self, 'requests','arn:aws:lambda:us-east-2:014498663421:layer:requests:1')
        

# Lambda Role



        lambda_role = iam.Role(
            self,
            "CustomLambdaRole",
            role_name="CustomLambdaRole",
            assumed_by=iam.ServicePrincipal("lambda.amazonaws.com")
        )

        # Inline Policy for Basic Execution Role
        lambda_role.add_to_policy(
            iam.PolicyStatement(
                actions=[
                    "logs:CreateLogGroup",
                    "logs:CreateLogStream",
                    "logs:PutLogEvents"
                ],
                resources=["*"]
            )
        )

        # Inline Policy for VPC Access Execution Role
        lambda_role.add_to_policy(
            iam.PolicyStatement(
                actions=[
                    "ec2:CreateNetworkInterface",
                    "ec2:DescribeNetworkInterfaces",
                    "ec2:DeleteNetworkInterface"
                ],
                resources=["*"]
            )
        )

        # Inline Policy for AWSLambdaExecute
        lambda_role.add_to_policy(
            iam.PolicyStatement(
                actions=[
                    "s3:PutObject",
                    "s3:GetObject",
                    "s3:ListBucket"
                ],
                resources=["*"]
            )
        )

        # Additional Policy for Invoking Lambda Functions
        lambda_role.add_to_policy(
            iam.PolicyStatement(
                actions=["lambda:InvokeFunction"],
                resources=["*"]
            )
        )





#ApiGateway



        api_name = f"{self.function_prefix}_api"
        api = apigw.RestApi(
            self,
            api_name,
            rest_api_name=api_name,
            default_cors_preflight_options={
                "allow_origins": apigw.Cors.ALL_ORIGINS,
                "allow_methods": apigw.Cors.ALL_METHODS,
                "allow_headers": [
                    "Content-Type",
                    "X-Amz-Date",
                    "Authorization",
                    "X-Api-Key",
                    "X-Amz-Security-Token",
                ],
            },
        )

        # Response Headers for Gateway Responses
        res_headers = {
            "Access-Control-Allow-Methods": "'GET,POST,PUT,DELETE,OPTIONS'",
            "Access-Control-Allow-Headers": "'Content-Type,X-Amz-Date,Authorization,X-Api-Key,X-Amz-Security-Token'",
            "Access-Control-Allow-Origin": "'*'",
        }

        # Gateway Responses
        api.add_gateway_response(
            "auth-response",
            type=apigw.ResponseType.ACCESS_DENIED,
            status_code="403",
            response_headers=res_headers,
            templates={
                "application/json": "{ 'message': '$context.error.messageString', 'statusCode': '403', 'type': '$context.error.responseType' }"
            },
        )
        api.add_gateway_response(
            "unauthorized",
            type=apigw.ResponseType.UNAUTHORIZED,
            status_code="401",
            response_headers=res_headers,
            templates={
                "application/json": "{ 'message': '$context.error.messageString', 'statusCode': '401', 'type': '$context.error.responseType' }"
            },
        )
        api.add_gateway_response(
            "value_type_error",
            type=apigw.ResponseType.DEFAULT_4_XX,
            status_code="400",
            response_headers=res_headers,
            templates={
                "application/json": "{ 'message': '$context.error.messageString', 'statusCode': '400', 'type': '$context.error.responseType' }"
            },
        )
        api.add_gateway_response(
            "server_error",
            type=apigw.ResponseType.DEFAULT_5_XX,
            status_code="500",
            response_headers=res_headers,
            templates={
                "application/json": "{ 'message': '$context.error.messageString', 'statusCode': '500', 'type': '$context.error.responseType' }"
            },
        )

        

# Lambdas


        authentication=self.create_function(name='authentication',layers=[jwt,bcrypt,mysql],timeout=20,environ=env,handler='auth.login',role=lambda_role)
        # authenticate - POST - /login
        self.add_resource(apigw,root_resource=api.root,resource_path='login',method='POST',lambda_function=authentication,auth=False)

        add_users=self.create_function(name='add_users',layers=[jwt,bcrypt,mysql],timeout=20,environ=env,handler='user.add_user',role=lambda_role)
        # authenticate - POST - /add-users
        self.add_resource(apigw,root_resource=api.root,resource_path='add-users',method='POST',lambda_function=add_users,auth=False)

        student_details = self.create_function(name='student_details',layers = [mysql], timeout=20, environ=env, handler = 'student_api.student_details',role = lambda_role)
        # Get student details - POST - /student
        student_resource=self.add_resource(apigw,root_resource=api.root,resource_path='student',method='POST',lambda_function=student_details,auth=False)

        add_student = self.create_function(name='add_student',layers = [mysql], timeout=20, environ=env, handler = 'student_api.add_student',role = lambda_role)
        # add new student - POST - /student/add
        self.add_resource(apigw,root_resource=student_resource,resource_path='add',method='POST',lambda_function=add_student,auth=False)

        payment = self.create_function(name='payment',layers = [mysql,requests], timeout=20, environ=env, handler = 'payment.payment_handler',role = lambda_role)
        # make payment - POST - /paid
        self.add_resource(apigw,root_resource=api.root,resource_path='paid',method='POST',lambda_function=payment,auth=False)

        query = self.create_function(name='query',layers = [mysql], timeout=20, environ=env, handler = 'student_api.testing_query',role = lambda_role)
        # make payment - POST - /query
        self.add_resource(apigw,root_resource=api.root,resource_path='query',method='POST',lambda_function=query,auth=False)
        
        count = self.create_function(name='count',layers = [mysql], timeout=20, environ=env, handler = 'student_api.count_student',role = lambda_role)
        # make payment - GET - /count
        self.add_resource(apigw,root_resource=api.root,resource_path='count',method='GET',lambda_function=count,auth=False)

        mark_payment = self.create_function(name='mark_payment',layers = [mysql,requests], timeout=20, environ=env, handler = 'payment.update_paid_status',role = lambda_role)
        # make payment - POST - /mark-paid
        self.add_resource(apigw,root_resource=api.root,resource_path='mark-paid',method='POST',lambda_function=mark_payment,auth=False)


#Functions

    def create_function(self, name, handler, layers, role, environ, timeout=3):
        lambda_function = _lambda.Function(
            self, name,
            runtime = _lambda.Runtime.PYTHON_3_12,
            code = _lambda.Code.from_asset(self.ASSET),
            handler = handler,
            function_name = f"{self.function_prefix}_{name}",
            layers = layers,
            environment = environ,
            role=role,
            vpc=self.vpc,
            security_groups = self.security_groups,
            timeout=Duration.seconds(timeout)
        )
        return lambda_function

    def add_resource(self, api_gateway, root_resource,resource_path, lambda_function=None, method=None,auth=True):
        resource = root_resource.add_resource(
            resource_path,
            default_cors_preflight_options=api_gateway.CorsOptions(
                allow_methods=api_gateway.Cors.ALL_METHODS,
                allow_origins=api_gateway.Cors.ALL_ORIGINS)
        )

        if method and lambda_function:
            if auth:
                resource.add_method(
                method.upper(),

                api_gateway.LambdaIntegration(
                    lambda_function,
                    proxy=True,
                    integration_responses=self.integration_responses,allow_test_invoke=False),method_responses=self.method_responses,authorizer=self.authorizer)
            else:
                resource.add_method(
                method.upper(),

                api_gateway.LambdaIntegration(
                    lambda_function,
                    proxy=True,
                    integration_responses=self.integration_responses,allow_test_invoke=False),method_responses=self.method_responses)
        
        return resource

    def add_method(self,api_gateway,resource,lambda_function=None,method=None,auth=True):
        if auth:
            resource.add_method(
            method.upper(),

            api_gateway.LambdaIntegration(
                lambda_function,
                proxy=True,
                integration_responses=self.integration_responses,allow_test_invoke=False),method_responses=self.method_responses,authorizer=self.authorizer)
        else:
            resource.add_method(method.upper(),
            api_gateway.LambdaIntegration(
                lambda_function,
                proxy=True,
                integration_responses=self.integration_responses,allow_test_invoke=False),method_responses=self.method_responses)
        return resource