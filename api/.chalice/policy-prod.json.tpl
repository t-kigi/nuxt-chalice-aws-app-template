{
  "Version": "2012-10-17",
  "Statement": [
    {
        "Sid": "IAMManagement",
        "Effect": "Allow",
        "Action": [
            "cognito-idp:ListUsersInGroup",
            "cognito-idp:ListUsers"
        ],
        "Resource": [
            "arn:aws:cognito-idp:ap-northeast-1:************:userpool/ap-northeast-1_**********"
        ]
    },
    {
        "Effect": "Allow",
        "Action": [
            "logs:CreateLogGroup",
            "logs:CreateLogStream",
            "logs:PutLogEvents"
        ],
        "Resource": "arn:aws:logs:*:*:*",
        "Sid": "CloudWatchLogsAccess"
    }
  ]
}
