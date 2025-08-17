# aws cloudformation delete-stack --stack-name AiexecAppStack
aws ecr delete-repository --repository-name aiexec-backend-repository --force
# aws ecr delete-repository --repository-name aiexec-frontend-repository --force
# aws ecr describe-repositories --output json | jq -re ".repositories[].repositoryName"